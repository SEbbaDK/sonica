module SonicaApi exposing (..)

import Json.Decode as D
import Json.Encode as E
import Dict exposing (Dict)

type alias SonicaMsg =
    { channel : Int
    , msgtype : String
    , value : Value
    }

type Value = VoidValue | ErrorValue String | SongValue Song | StatusValue Status

type alias Song =
    { title : String
    , artist : String
    , album : String
    }

type alias Status =
    { current : Song
    , length : Int
    , progress : Int
    , queueLength : Int
    , queueHash : Int
    , queue : List Song
    , autoplay : List Song
    }

--------------
-- DECODING --
--------------

errorDecoder = D.field "message" D.string
errorValueDecoder = errorDecoder
    |> D.andThen (\m -> D.succeed <| ErrorValue m)

songDecoder = D.map3 Song
    (D.field "title" D.string)
    (D.field "artist" D.string)
    (D.field "album" D.string)

songValueDecoder = songDecoder
    |> D.andThen (\s -> D.succeed <| SongValue s)

statusDecoder = D.map7 Status
    (D.field "current" songDecoder)
    (D.field "length" D.int)
    (D.field "progress" D.int)
    (D.field "queue_length" D.int)
    (D.field "queue_hash" D.int)
    (D.field "queue" (D.list songDecoder))
    (D.field "autoplay" (D.list songDecoder))

statusValueDecoder = statusDecoder
    |> D.andThen (\s -> D.succeed <| StatusValue s)

valueDecoder typeString = case typeString of
    "ReturnSong" -> songValueDecoder
    "ReturnStatus" -> statusValueDecoder
    "Return" -> D.succeed VoidValue
    "Error" -> errorValueDecoder
    _ -> D.fail <| "Can't do anything with type: " ++ typeString

--sonicaMsgDecoder : String -> SonicaMsg Int String String
sonicaMsgDecoder =
    D.field "type" D.string |> D.andThen (\t ->
        D.map3 SonicaMsg
            (D.field "channel" D.int)
            (D.succeed t)
            (D.field "value" <| valueDecoder t)
    )

decodeMsg = D.decodeString sonicaMsgDecoder

--------------
-- ENCODING --
--------------

sonicaPlayMsg channel = sonicaMsg "Play" [] channel
sonicaStopMsg channel = sonicaMsg "Stop" [] channel
sonicaStatusMsg channel queueMax autoplayMax =
    sonicaMsg "Status"
        [ ("queue_max", E.int queueMax)
        , ("autoplay_max", E.int autoplayMax)
        ]
        channel

sonicaMsg method value channel =
    E.encode 0 <| E.object
        [ ( "type", E.string method )
        , ( "channel", E.int channel )
        , ( "value", E.object value )
        ]

