#!/usr/bin/env python3

import cmd, mqtt
c = mqtt.client()
c.connect()
c.client.loop_start()

class Cli(cmd.Cmd):
    intro = 'Welcome to the ASSCAN admin shell. Type help or ? to list commands.\n'
    prompt = 'ASSCAN> '

    def do_list_agents(self, arg):
        'Lists connected clients'
        print(c.get_clients())

    def do_get_results_by_ip(self, arg):
        'Gets results for IP'
        c.result_by_type('ip', arg)

    def do_get_results_by_port(self, arg):
        'Gets results by port'
        c.result_by_type('port', arg)

    def do_everything(self, arg):
        'Gets all results'
        c.all_results()
        
    def do_bye(self, arg):
        print('bye bye')
        return True

    def do_EOF(self, arg):
        return True

if __name__=='__main__':
    Cli().cmdloop()

c.client.loop_stop()
    
