Discord Login On Landing Page
User Logs in
Show list of servers on left side, (kind of like how discord do)
When user clicks on a server, open the settings for that server (if they have permission?)

<ServerListForUser>
    prop: list of server objects
    <ServerDisplay>
        prop: a server object
        Server object has
            id
            name
            url for photo
        servers have two states, expanded and unexpanded
        When the server is expanded, we show the
        <ServerSettings>
            gets passed all of the variables
                Owns its own state from the db, loads the settings itself assuming this is possible
            <Timeout>
                hopefully the lowest fragment level
            <Roles>
                Needs more detail, 
