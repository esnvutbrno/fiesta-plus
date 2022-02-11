#!/usr/bin/env ruby

require 'git'
require 'logger'
require 'github/markup'
require 'elasticsearch'

require_relative 'wait-for-port'

PATH = "/usr/src/wiki"
# clone wiki repository local
git = Git.clone(
  'https://github.com/esnvutbrno/buena-fiesta.wiki.git',
  PATH,
  # :log => Logger.new(STDOUT)
)


wait_for_port('elastic', 9200)

elastic = Elasticsearch::Client.new(
  url: 'https://elastic:elastic@elastic:9200',
  transport_options: {
    ssl: { ca_file: '/usr/share/certs/rootCA.pem' }
  },
  log: true,
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
  last_commit = git.log(1).object(file).last

  puts file,
       last_commit.author.name,
       last_commit.author.email,
       last_commit.author.date,
       last_commit.message, language

  if language != nil
    # render into HTML
    rendered = GitHub::Markup.render(file, content)

    name = file[PATH.length + 1..]
    elastic.index(
      index: 'wiki',
      id: name,
      body: {
        content: rendered,
        file: name,
        last_change: {
          at: last_commit.date,
          name: last_commit.author.name,
          email: last_commit.author.email,
          sha: last_commit.sha,
        }
      }
    )
  end
  puts ''
end
