#!/usr/bin/env crystal

require "./sonica_services.pb.cr"
require "./sonica.pb.cr"

puts "Connecting"

sonica = Sonica::Stub.new "localhost", 7700

puts "Connected"

pp (sonica.play (Empty.new false))

