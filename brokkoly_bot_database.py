import psycopg2


class BrokkolyBotDatabase:
    def __init__(self, database_url):
        self.conn = psycopg2.connect(database_url, sslmode='require')

    def add_command(self, server_id, command, message, mod_only=False):
        """
        Adds a new command to the bot
        :param mod_only:
        :param server_id:
        :param command:
        :param message:
        :return:
        """
        cursor = self.conn.cursor()
        self.send_query(cursor, """
            SELECT * FROM COMMAND_LIST
            WHERE server_id = %s
                AND command_string = %s
                AND entry_value = %s;
                ;""",
                        (str(server_id), command, message))
        if cursor.rowcount > 0:
            print("That command already exists!\n", "Count=%d" % cursor.rowcount)
            cursor.close()
            return False
        self.send_query(cursor,
                        """INSERT INTO COMMAND_LIST (server_id, command_string, entry_value, mod_only) 
                        VALUES (%s,%s,%s,%s);""",
                        (str(server_id), command, message, 1 if mod_only else 0))
        cursor.close()
        self.conn.commit()
        return True

    def remove_command(self, server_id=None, command="", command_id=None):
        cursor = self.conn.cursor()
        if command_id:
            query = """
            DELETE FROM COMMAND_LIST
            WHERE command_id = %s;
            """
            params = (command_id,)
        else:
            query = """
            DELETE FROM COMMAND_LIST
            WHERE server_id = %s
                AND command_string = %s
            """
            params = (str(server_id), command)
        self.send_query(cursor, query, params)
        cursor.close()
        self.conn.commit()

    def get_all_commands(self, server_id):
        cursor = self.conn.cursor()
        self.send_query(cursor, """
            SELECT command_id,command_string,entry_value FROM COMMAND_LIST
            WHERE server_id=%s
            ORDER BY 
                command_string ASC,
                command_id ASC;
            
        """,
                        (str(server_id),))
        results = None
        if cursor.rowcount > 0:
            results = cursor.fetchall()
        cursor.close()
        return results

    def get_all_command_strings(self, server_id):
        cursor = self.conn.cursor()
        self.send_query(cursor, """
            SELECT DISTINCT command_string FROM COMMAND_LIST
            WHERE server_id=%s
            ORDER BY
                command_string ASC;
        """, (str(server_id),))
        results = None
        if cursor.rowcount > 0:
            results = cursor.fetchall()
        cursor.close()
        return results

    def get_all_responses_for_command(self, server_id, command):
        cursor = self.conn.cursor()
        self.send_query(cursor, """
            SELECT command_id,command_string,entry_value FROM COMMAND_LIST
            WHERE server_id=%s
                AND command_string = %s
            ORDER BY 
                command_string ASC,
                command_id ASC; 
        """,
                        (str(server_id), command))
        results = None
        if cursor.rowcount > 0:
            results = cursor.fetchall()
        return results

    def add_server(self, server_id, cooldown):
        # todo not sure about this
        server_id = str(server_id)
        if self.get_server_cooldown(server_id) >= 0:
            return
        if cooldown < 0:
            cooldown = 30
        cursor = self.conn.cursor()
        self.send_query(cursor,
                        """INSERT INTO SERVER_LIST (server_id, timeout_seconds) VALUES (%s, %s)""",
                        (server_id, cooldown))
        cursor.close()
        self.conn.commit()

    def get_all_servers(self):
        cursor = self.conn.cursor()
        self.send_query(cursor,
                        """
                        SELECT server_id FROM SERVER_LIST;
                        """)
        results = None
        if cursor.rowcount > 0:
            results = cursor.fetchall()
        cursor.close()
        return results

    # def set_server_details(self, server_id, server_name="", server_url=""):
    #     cursor = self.conn.cursor()
    #     self.send_query(cursor,
    #                     """
    #                     UPDATE SERVER_LIST
    #                     SET name = %s,
    #                         icon_url_64 = %s
    #                     WHERE server_id = %s;
    #                     """, (server_name, server_url, str(server_id)))
    #     cursor.close()
    #     self.conn.commit()

    def set_server_cooldown(self, server_id, cooldown):
        # todo implement set_server_timeout
        cursor = self.conn.cursor()
        self.send_query(cursor,
                        """
                        UPDATE SERVER_LIST
                        SET timeout_seconds = %s
                        WHERE SERVER_LIST.server_id=%s;
                        """, (cooldown, str(server_id)))
        cursor.close()
        self.conn.commit()
        return

    def get_server_cooldown(self, server_id):
        cursor = self.conn.cursor()
        self.send_query(cursor, """
                SELECT timeout_seconds FROM SERVER_LIST WHERE SERVER_LIST.server_id=%s""", (str(server_id),))
        result = cursor.fetchone()
        cursor.close()
        if not result:
            return -1
        # print(result[0])
        return result[0]

    def select_all(self):
        cursor = self.conn.cursor()
        self.send_query(cursor, """
        SELECT * FROM COMMAND_LIST
        """)

    def get_all_server_prefixes(self):
        cursor = self.conn.cursor()
        self.send_query(cursor, """
                SELECT server_id,command_prefix FROM SERVER_LIST;""")
        results = None
        if cursor.rowcount > 0:
            results = cursor.fetchall()
        cursor.close()
        return results

    def get_all_twitch_users(self, server_id=''):
        if server_id:
            return self.get_all_twitch_users_from_server(server_id)
        cursor = self.conn.cursor()
        self.send_query(cursor, """
                        SELECT channel_name,server_id,discord_user_id FROM twitch_users;""")
        results = None
        if cursor.rowcount > 0:
            results = cursor.fetchall()
        cursor.close()
        return results

    def get_twitch_user_for_server(self, server_id, channel_name, discord_user_id):
        server_id = str(server_id)
        discord_user_id = str(discord_user_id)
        cursor = self.conn.cursor()
        self.send_query(cursor, """SELECT channel_name,server_id,discord_user_id FROM twitch_users WHERE server_id=%s 
        AND (channel_name=%s OR discord_user_id=%s);""",
                        (server_id, channel_name, discord_user_id))
        results = None
        if cursor.rowcount > 0:
            results = cursor.fetchone()
        cursor.close()
        return results

    def get_all_twitch_users_from_server(self, server_id):
        if server_id:
            return self.get_all_twitch_users_from_server(server_id)
        cursor = self.conn.cursor()
        self.send_query(cursor, """
                                SELECT channel_name,server_id,discord_user_id FROM twitch_users WHERE server_id=%s;""",
                        (str(server_id),))
        results = None
        if cursor.rowcount > 0:
            results = cursor.fetchall()
        cursor.close()
        return results

    def add_twitch_user(self, server_id, channel_name, user_id):
        server_id = str(server_id)
        user_id = str(user_id)
        cursor = self.conn.cursor()
        self.send_query(cursor, """SELECT channel_name,server_id,discord_user_id FROM twitch_users WHERE server_id=%s 
        AND channel_name=%s;""",
                        (str(server_id), channel_name))
        if cursor.rowcount > 0:
            # Check if it's already there
            result = cursor.fetchone()
            if result[2] == user_id:
                return
            else:
                # Update the value
                self.send_query(cursor, """UPDATE twitch_users SET discord_user_id=%s WHERE server_id=%s AND 
                channel_name=%s;""",
                                (user_id, server_id, channel_name))
        else:
            self.send_query(cursor,
                            """INSERT INTO twitch_users (channel_name,server_id,discord_user_id) 
                            VALUES (%s, %s, %s);""",
                            (channel_name, server_id, user_id))
        cursor.close()
        self.conn.commit()

    def remove_twitch_user(self, server_id, channel_name="", user_id=""):
        server_id = str(server_id)
        user_id = str(user_id) or "0"
        channel_name = channel_name or "0"
        cursor = self.conn.cursor()
        self.send_query(cursor, """DELETE FROM twitch_users WHERE server_id=%s AND (channel_name=%s OR 
        discord_user_id=%s);""", (server_id, channel_name, user_id))
        cursor.close()
        self.conn.commit()

    def get_servers_for_twitch_user(self, username):
        cursor = self.conn.cursor()
        self.send_query(cursor, """SELECT server_id,discord_user_id FROM twitch_users WHERE channel_name=%s;""",
                        (username,))
        results = None
        if cursor.rowcount > 0:
            results = cursor.fetchall()
        cursor.close()
        return results

    def get_server_twitch_info(self, server_id):
        cursor = self.conn.cursor()
        self.send_query(cursor, """
                SELECT twitch_channel,twitch_live_role_id FROM SERVER_LIST WHERE SERVER_LIST.server_id=%s""",
                        (str(server_id),))
        result = cursor.fetchone()
        cursor.close()
        if not result:
            return None
        # print(result[0])
        return result

    def get_message(self, server_id, command, to_search, user_is_mod=False):
        """
        :param server_id:
        :param command:
        :param to_search:
        :return:
        """
        cursor = self.conn.cursor()
        if to_search:
            # TODO: use regex instead of like so that you can match on mixed case versions of the string.
            query = """
            SELECT entry_value
            FROM COMMAND_LIST
            WHERE server_id = %s
                AND command_string = %s
                AND entry_value ILIKE %s"""
            if not user_is_mod:
                query += "\nAND NOT mod_only=1\n"
            query += "ORDER BY RANDOM() LIMIT 1;"
            params = (str(server_id), command, "%%" + to_search + "%%")
        else:
            query = """
                    SELECT entry_value
                    FROM COMMAND_LIST
                    WHERE server_id=%s
                        AND command_string=%s"""
            if not user_is_mod:
                query += "\nAND NOT mod_only=1\n"
            query += "ORDER BY RANDOM() LIMIT 1;"
            params = (str(server_id), command)

        self.send_query(cursor, query, params)
        message = cursor.fetchone()
        cursor.close()
        if not message:
            return ""
        # print(message)
        return message[0]

    def create_tables(self):
        cursor = self.conn.cursor()
        self.send_query(cursor,
                        """
                        CREATE TABLE SERVER_LIST (
                            server_id VARCHAR PRIMARY KEY,
                            timeout_seconds int
                        );
                        CREATE TABLE COMMAND_LIST (
                            command_id int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                            server_id VARCHAR,
                            command_string varchar(50) NOT NULL,
                            entry_value varchar(1000) NOT NULL
                        );
                        CREATE INDEX command_index
                        ON COMMAND_LIST(server_id,command_string);
                        
                        CREATE TABLE TIMED_OUT_USERS (
                            timed_out_id int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                            server_id VARCHAR NOT NULL,
                            user_id bigint NOT NULL,
                            timeout_end bigint NOT NULL
                        );
                        """)
        cursor.close()
        self.conn.commit()

    def add_timed_out_users_table(self):
        cursor = self.conn.cursor()
        self.send_query(cursor,
                        """
                        CREATE TABLE TIMED_OUT_USERS (
                            timed_out_id int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                            server_id bigint NOT NULL,
                            user_id bigint NOT NULL,
                            timeout_end bigint NOT NULL
                        );
                        """)
        cursor.close()
        self.conn.commit()
        return

    def get_manager_role_for_server(self, server_id):
        cursor = self.conn.cursor()
        server_id = str(server_id)
        self.send_query(cursor,
                        """
                        SELECT bot_manager_role_id from SERVER_LIST
                        WHERE server_id=%s;  
                        """, (server_id,))
        results = None
        if cursor.rowcount > 0:
            results = cursor.fetchone()
        cursor.close()
        return results[0]

    def get_timeout_role_for_server(self, server_id):
        cursor = self.conn.cursor()
        server_id = str(server_id)
        self.send_query(cursor,
                        """
                        SELECT timeout_role_id from SERVER_LIST
                        WHERE server_id=%s;  
                        """, (server_id,))
        results = None
        if cursor.rowcount > 0:
            results = cursor.fetchone()
        cursor.close()
        return results[0]

    def add_timeout_role_for_server(self, server_id, role_id):
        cursor = self.conn.cursor()
        self.send_query(cursor,
                        """
                        UPDATE SERVER_LIST
                        SET timeout_role_id=%s
                        WHERE server_id=%s;  
                        """, (role_id, str(server_id)))
        cursor.close()
        self.conn.commit()

    def add_timeout_role_column(self):
        cursor = self.conn.cursor()
        self.send_query(cursor,
                        """
                        ALTER TABLE SERVER_LIST
                        ADD COLUMN timeout_role_id bigint;
                        """)
        cursor.close()
        self.conn.commit()

    def get_all_timeout_rows(self):
        cursor = self.conn.cursor()
        self.send_query(cursor,
                        """
                        SELECT server_id,user_id,timeout_end FROM TIMED_OUT_USERS;
                        """)
        results = None
        if cursor.rowcount > 0:
            results = cursor.fetchall()
        cursor.close()
        return results

    def add_user_timeout_to_database(self, server_id, user_id, until_time):
        cursor = self.conn.cursor()
        self.send_query(cursor,
                        """
                        INSERT INTO TIMED_OUT_USERS (server_id, user_id, timeout_end) VALUES (%s, %s, %s);
                        """, (str(server_id), user_id, until_time))
        cursor.close()
        self.conn.commit()

    def remove_user_timeout_from_database(self, server_id, user_id):
        cursor = self.conn.cursor()
        self.send_query(cursor,
                        """
                        DELETE FROM TIMED_OUT_USERS
                        WHERE server_id=%s
                        AND user_id=%s;
                        """, (str(server_id), user_id))
        cursor.close()
        self.conn.commit()

    def get_user_timeouts_finished(self, current_time):
        cursor = self.conn.cursor()
        self.send_query(cursor,
                        """
                        SELECT server_id,user_id,timeout_end FROM TIMED_OUT_USERS
                        WHERE timeout_end<=%s;
                        """, (current_time,))
        results = None
        if cursor.rowcount > 0:
            results = cursor.fetchall()
        cursor.close()
        return results

    def drop_command_list(self):
        cursor = self.conn.cursor()
        self.send_query(cursor,
                        """
                        DROP TABLE IF EXISTS COMMAND_LIST CASCADE;
                        """
                        )
        cursor.close()
        self.conn.commit()

    def drop_server_list(self):
        cursor = self.conn.cursor()
        self.send_query(cursor,
                        """
                        DROP TABLE IF EXISTS SERVER_LIST CASCADE;
                        """
                        )
        cursor.close()
        self.conn.commit()

    @staticmethod
    def send_query(cur, command, args=None):
        try:
            if args:
                cur.execute(command, args)
            else:
                cur.execute(command)

        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while executing command:\n", error)

    # def convert_from_map(self, command_map, timeout):
    #     for server_id in timeout:
    #         add_server(conn, server_id, timeout[server_id])
    #         for command in command_map:
    #             for entry in command_map[command]:
    #                 add_command(conn, server_id, command[1:], entry)
