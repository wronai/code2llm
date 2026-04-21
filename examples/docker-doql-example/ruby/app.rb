require 'json'
require 'webrick'

PORT = ENV.fetch('PORT', '8080').to_i
SERVICE_NAME = ENV.fetch('SERVICE_NAME', 'ruby-api')
DB_HOST = ENV.fetch('DB_HOST', 'database')

server = WEBrick::HTTPServer.new(
  Port: PORT,
  DocumentRoot: '/'
)

trap('INT') { server.shutdown }

server.mount_proc '/health' do |req, res|
  response = {
    message: 'OK',
    service: SERVICE_NAME,
    language: 'Ruby',
    version: '3.2',
    db_host: DB_HOST,
    ruby_version: RUBY_VERSION
  }
  
  res.content_type = 'application/json'
  res.body = response.to_json
end

server.mount_proc '/api' do |req, res|
  response = {
    message: 'Hello from Ruby service!',
    service: SERVICE_NAME,
    language: 'Ruby',
    version: '3.2',
    db_host: DB_HOST,
    ruby_version: RUBY_VERSION
  }
  
  res.content_type = 'application/json'
  res.body = response.to_json
end

puts "Ruby service listening on port #{PORT}"
server.start
