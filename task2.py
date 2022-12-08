#!/bin/env python3 
import sys
from math  import fabs, sqrt
import pandas as pd
from asyncio import sleep as sl
from loguru import logger
from random import randint, seed, uniform,normalvariate
import time
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from spade.template import Template
from spade import quit_spade

XMPP_server = "127.0.0.1"
Agent_prefix = "agent"

class MyAgent (Agent):
    def __init__(self, n, init_state, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = init_state
        self.neighs = n
        self.cycle = 0
        self.cur = []
        self.next = []
        self.alph = 0.1
        self.to_send = True
        self.ready = 0
        self.cur_send_n = 0
    class send_b(CyclicBehaviour):
        async def run(self):
            if (self.agent.to_send and self.agent.ready == 1):
                for n in self.agent.neighs:
                    msg = Message(to=n)
                    if (uniform(0, 1) > 0.15):
                        msg.body = str(self.agent.state + uniform(-0.1, 0.1))
                    else: 
                        msg.body = None
                    msg.thread = str(self.agent.cycle)
                    #print(f"{self.agent.name} send {msg}")
                    #self.agent.cur_send_n += 1
                    await sl(uniform(0, 0.0001))
                    await self.send(msg)
                    self.agent.cur_send_n += 1

            self.agent.to_send=False
    class recv_b(CyclicBehaviour):
        
        async def process_cur(self):
            #print(f"{self.agent.name} is at cycle {self.agent.cycle} sended {self.agent.cur_send_n}") 
            control = 0
            if (self.agent.cur_send_n != len(self.agent.neighs)):
                return 
            for m in self.agent.cur:
                if m.body is not None:
                    control += float(m.body) - self.agent.state
            control *= self.agent.alph
            self.agent.cycle += 1
            self.agent.state += control 
            self.agent.cur = self.agent.next.copy()
            self.agent.next = []
            self.agent.cur_send_n = 0
            self.agent.to_send = True

        async def check_if_cur_is_full(self):
            if len(self.agent.cur) == len(self.agent.neighs):
                await self.process_cur()

        async def run(self):
            msg = await self.receive(timeout=3)
            if (self.agent.ready == 0):
                self.agent.add_behaviour(self.agent.send_b())
                self.agent.ready = 1

            #if (True):
                #print(f"{self.agent.name} recv {msg}")
            if (msg is not None):
                
                msg_cycle = int(msg.thread)
        
                if (msg_cycle == self.agent.cycle):
                    if (msg not in self.agent.cur):
                        self.agent.cur.append(msg)
                elif (msg_cycle == self.agent.cycle+1):
                    if (msg not in self.agent.next):
                        self.agent.next.append(msg)
                else:
                    logger.error("desync detected\n exiting...")
                    quit_spade()
            await self.check_if_cur_is_full()
    class waiter_b(CyclicBehaviour):
        async def  run(self):
            #if (can_cont(self.agent)):
                #self.agent.add_behaviour(self.agent.recv_b())
                #self.agent.add_behaviour(self.agent.send_b())
            self.agent.add_behaviour(self.agent.send_b())
            self.agent.ready = 1

    async def setup(self):
        self.ready = 0
        self.add_behaviour(self.recv_b())
        #self.add_behaviour(self.send_b())

graph = [
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [1, 2, 3, 4, 17]],#0
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [0, 18]],         #1 
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [0, 6]],          #2 
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [0, 12]],         #3 
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [0, 5, 9]],       #4 
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [4]],             #5 
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [2, 7]],          #6 
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [6, 8, 9]],       #7 
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [7]],             #8 
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [4, 7, 10]],      #9 
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [9, 11]],         #10 
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [10]],            #11 
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [3, 13, 14]],     #12 
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [12]],            #13 
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [12, 15, 17]],    #14 
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [14, 17]],        #15 
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [17]],            #16 
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [14, 15,0, 16, 18]],#17
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [17, 1]],          #18
        ]
graph_ = [[f"{Agent_prefix}{1}@{XMPP_server}",f"{Agent_prefix}{2}@{XMPP_server}", f"{Agent_prefix}{3}@{XMPP_server}"],
         [f"{Agent_prefix}{0}@{XMPP_server}",f"{Agent_prefix}{2}@{XMPP_server}"],
         [f"{Agent_prefix}{1}@{XMPP_server}",f"{Agent_prefix}{0}@{XMPP_server}", f"{Agent_prefix}{3}@{XMPP_server}",f"{Agent_prefix}{5}@{XMPP_server}", f"{Agent_prefix}{6}@{XMPP_server}" ],
         [f"{Agent_prefix}{0}@{XMPP_server}", f"{Agent_prefix}{4}@{XMPP_server}",f"{Agent_prefix}{2}@{XMPP_server}"],
         [f"{Agent_prefix}{3}@{XMPP_server}"],
         [f"{Agent_prefix}{2}@{XMPP_server}",f"{Agent_prefix}{6}@{XMPP_server}",f"{Agent_prefix}{7}@{XMPP_server}"],
         [f"{Agent_prefix}{5}@{XMPP_server}",f"{Agent_prefix}{7}@{XMPP_server}", f"{Agent_prefix}{2}@{XMPP_server}"],
         [f"{Agent_prefix}{6}@{XMPP_server}", f"{Agent_prefix}{5}@{XMPP_server}"]

        ]
if __name__ == "__main__":
    s = 0
    agents = []
    seed(10) 
    for i in range(0, len(graph)):
        val = randint(0, 100)
        s += val
        agent = MyAgent(graph[i], val, f"{Agent_prefix}{i}@{XMPP_server}", "mypass", verify_security=False)
        agent.start()
        agents.append(agent)
    print(f"True average value is {(s)/len(graph)}")
    print("t to print stat table\nq to exit\nctrl^C to exit")
    while True:
        try:
            time.sleep(1)
            a = sys.stdin.read(1)
            if a == 't':
                data = {
                    "agent":[str(i.name).split("@")[0] for i in agents],
                    "state":[i.state for i in agents],
                    "cycle":[i.cycle for i in agents],
                    "err":[  fabs(i.state - s/len(graph)) for i in agents]
                    }
                print(f"Err = {sqrt(sum([(i.state - s/len(graph))**2 for i in agents])/len(graph))}")
                print(pd.DataFrame(data = data))
            elif a == 'q':
                for i in agents:
                    i.stop()
                break
        except KeyboardInterrupt:
            break
    quit_spade()
    print("Agents finished")
