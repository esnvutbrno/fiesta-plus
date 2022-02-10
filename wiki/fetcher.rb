#!/usr/bin/env ruby

require 'git'
require 'logger'
require 'github/markup'


PATH = "/usr/src/wiki"
# clone wiki repository local
g = Git.clone(
  'https://github.com/esnvutbrno/buena-fiesta.wiki.git',
  PATH,
  # :log => Logger.new(STDOUT)
)

# for all files in repository
Dir[PATH + '/**/*'].select {
  |f| File.file?(f)
}.each do |file|
  content = File.read(file)
  # try to detect language
  language = GitHub::Markup.language(file, content)
  # get latest change of file

  # @type Commit
  last_commit = g.log(1).object(file).last

  puts file,
       last_commit.author.name,
       last_commit.author.email,
       last_commit.author.date,
       last_commit.message, language

  if language != nil
    # render into HTML
    rendered = GitHub::Markup.render(file, content)
  end
  puts ''
end
