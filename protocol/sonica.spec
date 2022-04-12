protocol: sonica

roles: daemon client


on daemon client: play pause restart next

on daemon:
    status_query  -> status_answer
    search_query  -> search_result
    choice        -> { choice_progress+ choice_finish error }
    engines_query -> engine_list
    library       -> song_list

on client:
	exit
	queued

error:
    type : string
    message : string

status_query:
	queue_amount : int
	autoplay_amount : int

status_answer:
	queue : song[]
	autoplay : song[]

search_query:
	query : string
	engines : string[]

engine_result:
	engine : string
	results : <int, song>
search_result:
	results : engine_result[]

choice:
	id : int
choice_progress:
	int percentage
choice_finish:

engine_query: void
engine_list:
	engines : string[]

song_list:
	songs : song[]

song:
	artist : string
	title : string
	album : string

