#!/usr/bin/env ruby

require 'git'
require 'logger'
require 'github/markup'
require 'elasticsearch'
require 'html/pipeline'
require 'fileutils'
require 'facets/string/titlecase'

class String
  def titleize
    split(/(\W)/).map(&:capitalize).join
  end
end


require_relative 'wait-for-port'


PATH = "/usr/src/wiki"

FileUtils.rm_rf(PATH)

# clone wiki repository local
git = Git.clone(
  'https://github.com/esnvutbrno/buena-fiesta.wiki.git',
  PATH,
  # :log => Logger.new(STDOUT)
)

git.config('log.date', 'unix')

wait_for_port('elastic', 9200)

elastic = Elasticsearch::Client.new(
  url: 'https://elastic:elastic@elastic:9200',
  transport_options: {
    ssl: { ca_file: '/usr/share/certs/rootCA.pem' }
  },
  log: true,
)

render_pipeline = HTML::Pipeline.new [
    HTML::Pipeline::TableOfContentsFilter,
    HTML::Pipeline::EmojiFilter,
]

# for all files in repository
Dir[PATH + '/**/*'].select {
  |f| File.file?(f)
}.each do |filepath|
  content = File.read(filepath)
  # try to detect language
  language = GitHub::Markup.language(filepath, content)
  # get latest change of file

  # @type Commit
  last_commit = git.log(1).object(filepath).last

  puts filepath,
       last_commit.author.name,
       last_commit.author.email,
       last_commit.author.date,
       last_commit.message, language

  if language != nil
    # render into HTML
    rendered = GitHub::Markup.render(filepath, content)

    # https://github.com/gjtorikian/html-pipeline#examples
    result = {}
    render_pipeline.call(
        rendered,
        {
            :anchor_icon => '<svg class="Wiki__link-icon" viewBox="0 0 16 16" version="1.1" aria-hidden="true"><path fill-rule="evenodd" d="M7.775 3.275a.75.75 0 001.06 1.06l1.25-1.25a2 2 0 112.83 2.83l-2.5 2.5a2 2 0 01-2.83 0 .75.75 0 00-1.06 1.06 3.5 3.5 0 004.95 0l2.5-2.5a3.5 3.5 0 00-4.95-4.95l-1.25 1.25zm-4.69 9.64a2 2 0 010-2.83l2.5-2.5a2 2 0 012.83 0 .75.75 0 001.06-1.06 3.5 3.5 0 00-4.95 0l-2.5 2.5a3.5 3.5 0 004.95 4.95l1.25-1.25a.75.75 0 00-1.06-1.06l-1.25 1.25a2 2 0 01-2.83 0z"></path></svg>',
            # TODO: well, GH or self-hosted?
            :asset_root => "https://github.githubassets.com/images/icons/"
        },
        result
    )

    filename = filepath[PATH.length + 1..]

    basename = File.basename(filename, File.extname(filename))
    title = basename.gsub("-", " ").titleize

    elastic.index(
      index: 'wiki',
      id: filename,
      body: {
        content: result[:output].to_s,
        toc: result[:toc],
        title: title,
        file: filename,
        last_change: {
            # 2022-02-11 10:40:58 +0000
          at: last_commit.date.iso8601,
          name: last_commit.author.name,
          email: last_commit.author.email,
          sha: last_commit.sha,
          parent_sha: last_commit.parent.sha,
        }
      }
    )
  end
  puts ''
end
