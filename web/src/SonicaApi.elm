module SonicaApi exposing (..)

import Json.Decode as D
import Json.Encode as E

type SonicaMsg token return text = Success token return | Failure token text | Error text

typeDecoder = D.field "type" D.string
tokenDecoder = D.field "token" D.int
valueDecoder = D.field "value" D.string

sonicaMsgDecoder : String -> SonicaMsg Int String String
sonicaMsgDecoder i =
    Error (Debug.log "decoded json" i)
--    case (D.decodeString (typeDecoder) i) of
--        Ok "error" -> Error (tokenDecoder i) (valueDecoder i)
--        Ok "return" -> Success (tokenDecoder i) (valueDecoder i)
--        Err -> Error (tokenDecoder

sonicaPlayMsg token = sonicaMsg "Play" "{}" token
sonicaStopMsg token = sonicaMsg "Stop" "{}" token

sonicaMsg method value token =
    "{ \"method\" : \"" ++ method ++ "\", \"value\" : " ++ value ++ ", \"token\" : " ++ String.fromInt token ++ " }"
