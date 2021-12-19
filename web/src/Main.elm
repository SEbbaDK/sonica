port module Main exposing (..)

import Browser
import Browser.Events exposing (onResize)
import Browser.Dom as Dom
import List exposing (map)
import Tuple exposing (first, second)

import Element exposing
    (el, row, column, text, rgb, width, fill, height, padding, spacing, fillPortion, px)
import Element.Input as Input
import Element.Background exposing (color)
import Element.Font as Font
import Element.Border as Border

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
    Sub.batch
        [ input Recv
        , onResize Resize
        ]

type alias Model =
    { state : PlayState
    , errors : List String
    , search: String
    , size: { width: Int, height: Int }
    }

nocmd : Model -> ( Model, Cmd Msg )
nocmd model = ( model, Cmd.none )

init : ( Int, Int ) -> ( Model, Cmd Msg )
init flag = nocmd
    { state = Stopped
    , errors = []
    , search = ""
    , size = { height = first flag, width = second flag }
    }

type Msg
    = Play
    | Pause
    | Stop
    | Recv String
    | EnterSearch String
    | Resize Int Int

update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        Play ->
            ( { model | state = Playing }
            , sonicaPlayMsg 0 |> Debug.log "sent message" |> output
            )

        Pause ->
            nocmd { model | state = Paused }

        Stop ->
            ( { model | state = Stopped }
            , sonicaStopMsg 0 |> output
            )

        Recv text ->
            case decodeMsg text of
                Ok v  -> nocmd { model | errors = model.errors ++ [ Debug.toString v ] }
                Err t -> nocmd { model | errors = model.errors ++ [ "decodeerr in (" ++ text ++"): " ++ Debug.toString t ] }
--            case (sonicaMsgDecoder text) of
--                Success token value ->
--                    nocmd model
--
--                Failure token value ->
--                    nocmd { model | errors = model.errors ++ [ value ] }
--
--                Error message ->
--                    nocmd model

        EnterSearch text ->
            nocmd { model | search = text }

        Resize width height ->
            nocmd { model | size = { width = width, height = height } }

-----------
-- VIEWS --
-----------

viewPlaypauseButton state =
    if state /= Playing
        then
            Input.button [] { label = text "▶", onPress = Just Play }
        else
            Input.button [] { label = text "⏹", onPress = Just Stop }

viewPlayButtons state =
    el [ Font.size 25 ] <| row [ spacing 5 ]
        [ viewPlaypauseButton state
        --, Input.button [] { label = text "⏹", onPress = Just Stop }
        ]

viewBar state =
    el [ color (rgb 1 0 0), width fill, padding 5 ] <|
        row []
            [ viewPlayButtons state
            ]

viewErrors model =
    column
        [ width <| px <| model.size.width // 2
        , color (rgb 0 0 1)
        ] <|
        map (\e -> text e) model.errors

viewSearch model =
    column [ width <| px <| model.size.width // 2, color (rgb 0 1 1)
            , height fill
            ]
        [ Input.text
            [ width fill
            , Element.alignTop
            ]
            { text = model.search
            , onChange = EnterSearch
            , label = Input.labelHidden "search"
            , placeholder = Just <| Input.placeholder [] <| text "Search"
            }
        , text model.search
        ]

viewApp model =
    el [ width <| px <| model.size.width, height fill, Element.scrollbarY ] <|
        row []
            [ viewErrors model
            , viewSearch model
            ]

view model =
    Element.layout [ width fill, height fill ] <|
        column [ width fill, height fill ]
            [ viewApp model
            , viewBar model.state
            ]

