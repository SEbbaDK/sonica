#!/usr/bin/env crystal

require "grpc"
require "./sonica_services.pb.cr"
require "./sonica.pb.cr"

class SonicaHandler < Sonica
    def play(empty : Empty) : Result
        puts "play"
        Result.new
    end
    
    def stop(empty : Empty) : Result
        puts "stop"
        Result.new
    end
    
    def skip(empty : Empty) : Result
        puts "skip"
        Result.new
    end
    
    def queue(hash : Queue::Hash) : Result
        puts "queue"
        Result.new
    end
    
    def clear(hash : Queue::Hash) : Result
        puts "clear"
        Result.new
    end
    
    def shuffle(hash : Queue::ShuffleTargets) : Result
        puts "shuffle"
        Result.new
    end
    
    def move(hash : Queue::Pair) : Result
        puts "move"
        Result.new
    end
    
    def remove(hash : Queue::Target) : Result
        puts "remove"
        Result.new
    end
    
    def search(hash : Search::Query) : Search::Result
        puts "search"
        Search::Result.new
    end
    
    def choose(choice : Search::Choice) : Result
        puts "choose"
        Result.new
    end
    
    def engines(r : Empty) : EngineList
        puts "engines"
        EngineList.new
    end
    
    def status(r : Status::Query) : Status::Info
        puts "status"
        Status::Info.new
    end
    
    def library(r : Empty) : LibraryInfo
        puts "library"
        LibraryInfo.new
    end
end

grpc = GRPC::Server.new
grpc << SonicaHandler.new

server = HTTP2::ClearTextServer.new [grpc]
server.listen "0.0.0.0", 7700

