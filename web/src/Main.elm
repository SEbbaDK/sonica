port module Main exposing (..)

import Browser
import Browser.Events exposing (onResize)
import Browser.Dom as Dom
import List exposing (map)
import Tuple exposing (first, second)
import Time exposing (every)
import Maybe exposing (withDefault, andThen)
import Dict

import Element exposing
    (Element, el, row, column, text, paragraph, image
    , rgb, width, fill, height, padding, spacing, fillPortion, px)
import Element.Input as Input
import Element.Background exposing (color)
import Element.Font as Font
import Element.Border as Border

import Json.Decode as Decode
import Html.Events

import SonicaApi exposing (..)

type PlayState = Playing | Stopped

main =
  Browser.element
    { init = init
    , update = update
    , view = view
    , subscriptions = subscriptions
    }

port input : (String -> msg) -> Sub msg
port output : String -> Cmd msg

requestStatus =
    sonicaStatusMsg 1 -1 -1 |> Debug.log "status request" |> output

subscriptions : Model -> Sub Msg
subscriptions _ =
    Sub.batch
        [ input Recv
        , onResize Resize
        , every 5000 (\_ -> RequestStatus)
        ]

type alias Model =
    { state : PlayState
    , errors : List String
    , search : String
    , size : { width: Int, height: Int }
    , status : Maybe Status
    , results : List EngineSearchResult
    }

nocmd : Model -> ( Model, Cmd Msg )
nocmd model = ( model, Cmd.none )

init : ( Int, Int ) -> ( Model, Cmd Msg )
init flag =
    ( { state = Stopped
      , errors = []
      , search = ""
      , size = { width = first flag, height = second flag }
      , status = Nothing
      , results = []
      }
    , requestStatus
    )

type Msg
    = Play
    | Stop
    | Skip
    | Recv String
    | Search
    | EnterSearch String
    | Resize Int Int
    | RequestStatus
    | Choose String

update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        Play ->
            ( { model | state = Playing }
            , sonicaPlayMsg 0 |> output
            )

        Stop ->
            ( { model | state = Stopped }
            , sonicaStopMsg 0 |> output
            )

        Skip ->
            ( model
            , sonicaSkipMsg 0 |> output
            )

        Recv text ->
            case decodeMsg text of
                Ok v  -> case v.value of
                    SearchValue r -> nocmd { model | results = r }
                    StatusValue s -> { model | status = Just s }
                        |> \m -> { m | state = (if s.current == Nothing then Stopped else Playing) }
                        |> nocmd
                    ErrorValue e -> nocmd { model | errors = e :: model.errors }
                    VoidValue -> nocmd model

                Err t -> nocmd { model | errors = model.errors ++ [ "decodeerr in (" ++ text ++"): " ++ Debug.toString t ] }

        Search ->
            ( model, sonicaSearchMsg 2 model.search |> Debug.log "search" |> output )

        EnterSearch text ->
            nocmd { model | search = Debug.log "s" text }

        Resize width height ->
            nocmd { model | size = { width = width, height = height } }

        RequestStatus ->
            ( Debug.log "Requst" model, requestStatus )

        Choose key ->
            ( { model | results = [] }, sonicaChooseMsg 3 key False |> Debug.log "choose" |> output )

-----------
-- VIEWS --
-----------

onEnter msg =
    Element.htmlAttribute
        (Html.Events.on "keyup"
            (Decode.field "key" Decode.string
                |> Decode.andThen
                    (\key ->
                        if key == "Enter" then
                            Decode.succeed msg

                        else
                            Decode.fail "Not the enter key"
                    )
            )
        )

barHeight = 40
sidebarWidth = 150
appPadding = 10
narrow model = model.size.width < 900
mainWidth model = model.size.width - sidebarWidth
mainColumnWidth model = mainWidth model // (if narrow model then 1 else 2)

viewPlaypauseButton state =
    if state /= Playing
        then
            Input.button [] { label = text "▶", onPress = Just Play }
        else
            Input.button [] { label = text "⏹", onPress = Just Stop }

viewPlayButtons state =
    el [ Font.size 25 ] <| row [ spacing 5 ]
        [ viewPlaypauseButton state
        , Input.button [] { label = text "⏭", onPress = Just Skip }
        --, Input.button [] { label = text "⏹", onPress = Just Stop }
        ]

viewSong : Maybe Song -> Element Msg
viewSong maybeSong =
    paragraph [ padding 3 ] <| case maybeSong of
        Just song ->
            [ text song.title
            , el [ Element.alpha 0.25 ] <| text " – "
            , el [ Element.alpha 0.66 ] <| text song.artist
            -- ] ++ if song.album == "" then [] else
            -- [ text " ["
            -- , text song.album
            -- , text "]"
            ]
        Nothing ->
            []

viewBar model = el
    [ color (rgb 0.8 0.2 0)
    , Font.color (rgb 0.95 0.95 0.95)
    , width fill
    , padding 5
    , height <| px barHeight
    ] <| row [ spacing 10 ]
        [ viewPlayButtons model.state
        , model.status |> andThen (\s -> s.current) |> viewSong
        ]

viewErrors model =
    if List.isEmpty model.errors
    then Element.none
    else column
        [ width <| px <| mainColumnWidth model
        , color (rgb 1 0 0)
        , padding appPadding
        ]
        <| map (\e -> paragraph [] [text e]) model.errors

viewSongListItem song = el
    [ color (rgb 0.9 0.9 0.9)
    , width fill
    , padding 5
    , Font.size 16
    ]
    (Just song |> viewSong)
    

viewSongList : String -> List Song -> Element Msg
viewSongList header songs =
    column [ spacing 10, padding 10, width fill ]
        [ el [ Font.size 30 ] <| text header
        , column [ spacing 5, width fill ] <| map (viewSongListItem) songs
        ]

viewQueue : Model -> Element Msg
viewQueue model =
    column
        [ width <| px <| mainColumnWidth model
        , padding appPadding
        ]
        <| case model.status of
            Just status ->
                [ viewSongList "Queue" status.queue
                , viewSongList "Autoplay" status.autoplay
                ]
            Nothing ->
                []

viewSearchResultItem key song =
    Input.button []
        { label = viewSong <| Just song
        , onPress = Just <| Choose key
        }

viewSearchResult : EngineSearchResult -> Element Msg
viewSearchResult result =
    column [ padding 10 ] <|
        [ el [ Font.size 24, Font.bold ] <| text result.name ] ++
        Dict.foldl
            (\k -> \v -> \l -> (viewSearchResultItem k v) :: l)
            []
            result.possibilities

viewSearchResults : Model -> List (Element Msg)
viewSearchResults model =
    [ column [ color (rgb 0.9 0.9 0.9) ] <|
        map (viewSearchResult) model.results
    ]

viewSearch model =
    column
        [ width <| px <| mainColumnWidth model
        , height fill
        , padding appPadding
        , onEnter Search
        ] <|
        [ Input.search
            [ width fill
            ]
            { text = model.search
            , onChange = EnterSearch
            , label = Input.labelHidden "search"
            , placeholder = Just <| Input.placeholder [] <| text "Search"
            }
        ]
        ++ viewSearchResults model

viewSidebar model = column
    [ color (rgb 0.9 0.9 0.9)
    , height fill
    , width <| px sidebarWidth
    ]
    [ column [ padding 10, width fill ] [ el [ Font.size 30, Font.family [ Font.serif ], Font.bold, Element.centerX ] <| text "Sonica" ]
    , image
        [ width fill
        , Element.alignBottom
        ]
        { src = "../media/avatar-transparent.png"
        , description = "Sonica Avatar"
        }
    ]

viewMain model = el
    [ width <| px <| model.size.width - sidebarWidth
    , height fill
    , Element.scrollbarY
    --, padding 20
    ] <| (if narrow model then column else row) []
        [ viewSearch model
        , column []
            [ viewErrors model
            , viewQueue model
            ]
        ]

viewApp model = row
    [ height <| px <| model.size.height - barHeight
    , width <| px <| model.size.width
    ]
    [ viewSidebar model
    , viewMain model
    ]

viewElement : Model -> Element Msg
viewElement model =
    column [ width fill, height fill ]
        [ viewApp model
        , viewBar model
        ]

view model =
    Element.layout
        [ width <| px model.size.width
        , height <| px model.size.height
        ] <| viewElement model

