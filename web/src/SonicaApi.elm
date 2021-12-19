module SonicaApi exposing (..)

import Json.Decode as D
import Json.Encode as E
import Dict exposing (Dict)

type alias SonicaMsg =
    { channel : Int
    , msgtype : String
    , value : Value
    }

type Value = VoidValue
           | ErrorValue String
           | StatusValue Status
           | SearchValue (List EngineSearch)

type alias Song =
    { title : String
    , artist : String
    , album : String
    }

type alias Status =
    { current : Maybe Song
    , length : Int
    , progress : Int
    , queueLength : Int
    , queueHash : Int
    , queue : List Song
    , autoplay : List Song
    }

type alias EngineSearch =
    { name : String
    , possibilities : Dict String Song
    }

type alias Search =
    { results : List EngineSearch
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

songMaybeDecoder = songDecoder
    |> D.andThen (\s -> D.succeed <|
        if s.title == "" then Nothing else Just s
    )

statusDecoder = D.map7 Status
    (D.field "current" songMaybeDecoder)
    (D.field "length" D.int)
    (D.field "progress" D.int)
    (D.field "queue_length" D.int)
    (D.field "queue_hash" D.int)
    (D.field "queue" (D.list songDecoder))
    (D.field "autoplay" (D.list songDecoder))

statusValueDecoder = statusDecoder
    |> D.andThen (\s -> D.succeed <| StatusValue s)

engineSearchDecoder = D.map2 EngineSearch
    (D.field "name" D.string)
    (D.field "possibilities" (D.dict songDecoder))

searchDecoder = D.field "results" (D.list engineSearchDecoder)

searchValueDecoder = searchDecoder
    |> D.andThen (\s -> D.succeed <| SearchValue s)

valueDecoder typeString = case typeString of
    "ReturnStatus" -> statusValueDecoder
    "ReturnSearch" -> searchValueDecoder
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

sonicaSearchMsg channel search =
    sonicaMsg "Search"
        [ ("query", E.list E.string [ search ])
        , ("engines", E.list E.string [])
        ]
        channel

sonicaMsg method value channel =
    E.encode 0 <| E.object
        [ ( "type", E.string method )
        , ( "channel", E.int channel )
        , ( "value", E.object value )
        ]

