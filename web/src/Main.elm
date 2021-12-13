port module Main exposing (..)

import Browser
import Html exposing (Html, button, div, text)
import Html.Events exposing (onClick)
import List exposing (map)

import SonicaApi exposing (..)

type PlayState = Playing | Paused | Stopped

main =
  Browser.element
    { init = init
    , update = update
    , view = view
    , subscriptions = subscriptions
    }

port input : (String -> msg) -> Sub msg
port output : String -> Cmd msg

subscriptions : Model -> Sub Msg
subscriptions _ =
    input Recv

type alias Model =
    { state : PlayState
    , errors : List String
    }

nocmd : Model -> ( Model, Cmd Msg )
nocmd model = ( model, Cmd.none )

init : () -> ( Model, Cmd Msg )
init flags = nocmd
    { state = Stopped
    , errors = [ ]
    }

type Msg
    = Play
    | Pause
    | Stop
    | Recv String

update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        Play ->
            ( { model | state = Playing }
            , sonicaPlayMsg 0 |> output
            )

        Pause ->
            nocmd { model | state = Paused }

        Stop ->
            ( { model | state = Stopped }
            , sonicaStopMsg 0 |> output
            )

        Recv text ->
            case (sonicaMsgDecoder text) of
                Success token value ->
                    nocmd model

                Failure token value ->
                    nocmd { model | errors = model.errors ++ [ value ] }

                Error message ->
                    nocmd model


viewPlaybutton state =
    if state /= Playing
    then
        button [ onClick Play ] [ text "▶" ]
    else
        button [ onClick Pause ] [ text "⏸" ]

view model =
    div []
        [ div [] (map (\s -> div [] [ text s ]) model.errors)
        , viewPlaybutton model.state
        , button [ onClick Stop ] [ text "⏹" ]
        --, div [] [ text (String.fromInt model) ]
        ]
