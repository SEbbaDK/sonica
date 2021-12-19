module SonicaApi exposing (..)

import Json.Decode as D
import Json.Encode as E
import Dict exposing (Dict)

--type SonicaMsg channel return text
--    = Success channel return
--    | Error channel text
--    | JsonError text

type alias SonicaMapMsg =
    { msgtype : String
    , channel : Int
    , value : Dict String String
    }

typeDecoder = D.field "type" D.string
channelDecoder = D.field "channel" D.int
valueDecoder = D.field "value" D.string

--sonicaMsgDecoder : String -> SonicaMsg Int String String
sonicaMsgDecoder =
    D.map3 SonicaMapMsg
        (D.at ["type"] D.string)
        (D.at ["channel"] D.int)
        (D.at ["value"] (D.dict D.string))

--    case typeDecoder i of
--        Ok "error" -> Error (channelDecoder i) (valueDecoder i)
--        Ok "return" -> Success (channelDecoder i) (valueDecoder i)
--        Err message -> JsonError message

decodeMsg = D.decodeString sonicaMsgDecoder

sonicaPlayMsg channel = sonicaMsg "Play" (Dict.empty) channel
sonicaStopMsg channel = sonicaMsg "Stop" (Dict.empty) channel

sonicaMsg : String -> Dict String String -> Int -> String
sonicaMsg method value channel =
    E.encode 0 <| E.object
        [ ( "type", E.string method )
        , ( "channel", E.int channel )
        , ( "value", E.dict identity E.string value )
        ]

