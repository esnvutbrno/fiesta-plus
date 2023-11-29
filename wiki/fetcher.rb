#!/usr/bin/env ruby

require "git"
require "logger"
require "linguist"
require "github/markup"
require "html/pipeline"
require "fileutils"
require "facets/string/titlecase"
require "sanitize"
require "sqlite3"

class String
  def titleize
    split(/(\W)/).map {
      |w|
      # firsth two chars is uppercase, so probably a abbreviation, so no capitalizing
      if w.match(/([A-Z][A-Z][a-z]*)/) then w else w.capitalize end
    }.join
  end
end

class VersionedImagesFilter < HTML::Pipeline::Filter
  def call
    doc.search("img").each do |img|
      next if img["src"].nil?
      src = img["src"].strip
      next if src.start_with?("http") or src.start_with?("//")

      img["src"] = src + "?v=" + context[:revision][..6]
    end
    doc
  end
end

WIKI_REPO_PATH = "/usr/src/wiki"

FileUtils.rm_rf(WIKI_REPO_PATH)
FileUtils.rm_rf(File.join(ENV["WIKI_STATIC_PATH"], "*"))

# clone wiki repository local
git = Git.clone(
  ENV["WIKI_GIT_URL"],
  WIKI_REPO_PATH,
  :log => Logger.new(STDOUT)
)

db_file = File.join(ENV["WIKI_STATIC_PATH"], "wiki.sqlite3")
File.delete(db_file) if File.exist?(db_file)

db = SQLite3::Database.new db_file

# Create a table
db.execute <<-SQL
  CREATE VIRTUAL TABLE IF NOT EXISTS
    wiki USING
    fts5(file, title, content_html, content_plain, toc, last_change);
SQL

git.config("log.date", "unix")

last_revision = git.object("HEAD^").sha

rich_pipeline = HTML::Pipeline.new [
  HTML::Pipeline::TableOfContentsFilter,
  VersionedImagesFilter,
  HTML::Pipeline::AbsoluteSourceFilter,
  HTML::Pipeline::AutolinkFilter,
  HTML::Pipeline::EmojiFilter,
]

md_pipeline = HTML::Pipeline.new [
  HTML::Pipeline::MarkdownFilter,
] + rich_pipeline.filters

# for all files in repository
Dir[WIKI_REPO_PATH + "/**/*"].select {
  |f|
  File.file?(f)
}.each do |filepath|
  content = File.read(filepath)
  # try to detect language
  language = GitHub::Markup.language(filepath, content)
  # get latest change of file

  # @type Commit
  last_commit = git.log(1).object(filepath).last

  relativepath = filepath[WIKI_REPO_PATH.length + 1..]

  context = {
    :anchor_icon => '<svg class="Wiki__link-icon" viewBox="0 0 16 16" version="1.1" aria-hidden="true"><path fill-rule="evenodd" d="M7.775 3.275a.75.75 0 001.06 1.06l1.25-1.25a2 2 0 112.83 2.83l-2.5 2.5a2 2 0 01-2.83 0 .75.75 0 00-1.06 1.06 3.5 3.5 0 004.95 0l2.5-2.5a3.5 3.5 0 00-4.95-4.95l-1.25 1.25zm-4.69 9.64a2 2 0 010-2.83l2.5-2.5a2 2 0 012.83 0 .75.75 0 001.06-1.06 3.5 3.5 0 00-4.95 0l-2.5 2.5a3.5 3.5 0 004.95 4.95l1.25-1.25a.75.75 0 00-1.06-1.06l-1.25 1.25a2 2 0 01-2.83 0z"></path></svg>',
    # TODO: well, GH or self-hosted?
    # https://github.com/WebpageFX/emoji-cheat-sheet.com/tree/master/public/graphics/emojis
    :asset_root => ENV["WIKI_STATIC_ASSETS_URL"],
    :image_base_url => ENV["WIKI_STATIC_URL"],
    :image_subpage_url => ENV["WIKI_STATIC_URL"],
    :revision => last_revision,
    :gfm => true,
  }

  if language == nil
    output_filepath = File.join(ENV["WIKI_STATIC_PATH"], relativepath)
    puts "To static: " + output_filepath
    FileUtils.makedirs(File.dirname(output_filepath))
    FileUtils.cp(filepath, output_filepath)
  else
    rich_result = {}

    # render into HTML
    # https://github.com/gjtorikian/html-pipeline#examples
    puts language.class
    if language == Linguist::Language['Markdown']
      # special pipeline for markdown
      out = {}
      md_pipeline.call(
        content,
        context,
        rich_result,
      )
    else
      rendered = GitHub::Markup.render(filepath, content)
      rich_pipeline.call(
        rendered,
        context,
        rich_result
      )
    end

    puts relativepath #,
#          last_commit.author.name,
#          last_commit.author.email,
#          last_commit.author.date,
#          last_commit.message, language

    basename = File.basename(relativepath, File.extname(relativepath))
    title = basename.gsub("-", " ").titleize

    db.execute(
        "INSERT INTO
        wiki (file, title, content_html, content_plain, toc, last_change)
        VALUES (?, ?, ?, ?, ?, ?)",
        [
            relativepath,
            title,
            rich_result[:output].to_s,
            Sanitize.fragment(rich_result[:output].to_s),
            rich_result[:toc],
            {
                # 2022-02-11 10:40:58 +0000
                at: last_commit.date.iso8601,
                name: last_commit.author.name,
                email: last_commit.author.email,
                sha: last_commit.sha,
                parent_sha: last_commit.parent.sha,
            }.to_json
        ]
    )

#     elastic.index(
#       index: "wiki",
#       id: relativepath,
#       body: {
#         content_html: rich_result[:output].to_s,
#         content_plain: Sanitize.fragment(rich_result[:output].to_s),
#         toc: rich_result[:toc],
#         title: title,
#         file: relativepath,
#         last_change: {
#           # 2022-02-11 10:40:58 +0000
#           at: last_commit.date.iso8601,
#           name: last_commit.author.name,
#           email: last_commit.author.email,
#           sha: last_commit.sha,
#           parent_sha: last_commit.parent.sha,
#         },
#       },
#     )


  end
  puts ""
end
