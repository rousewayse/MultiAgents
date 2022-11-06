#!/bin/env python 
from random import randint
import time
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from spade.template import Template
from spade import quit_spade
XMPP_server = "127.0.0.1"
class MyAgent(Agent):
    #extending Agent constructor to define MyAgent neighbours in graph
    #super returns a proxy parent object
    def __init__(self, neighbours=[], ifleader = False, value: int = 0,   *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.neighbours = neighbours
        self.parent_jid = None
        self.leader = ifleader
        if (self.leader):
            self.parent_jid = self.name
        self.childs = []
        self.value = value
        self.counter = 0
        self.childs_values = []
        self.has_on_send_value_behaviour = False
        self.messages = 0;

    def stop(self):
        print(self.name + f" sent {self.messages} messages and used {len(self.neighbours) + 2 + len(self.childs) + len(self.childs_values)} memory cells" );
        return super().stop()

    class on_make_child_reply(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if (msg):
                if (self.agent.parent_jid is None):
                    self.agent.parent_jid = str(msg.sender).split('@')[0]
                    msg = msg.make_reply()
                    msg.set_metadata("action", "answer")
                    msg.body = "True"
                    if (self.agent.leader == False):
                        self.agent.add_behaviour(self.agent.send_make_child())
                        
                else:
                    msg.make_reply()
                    msg.set_metadata("action", "answer")
                    msg.body = ""
                await self.send(msg)
                self.agent.messages += 1

    class send_make_child(OneShotBehaviour):
        async def run(self):
            for i in self.agent.neighbours:
                if (i != self.agent.parent_jid):
                    msg = Message(to=i+"@"+XMPP_server)
                    msg.set_metadata("action", "make_child")
                    await self.send(msg)
                    self.agent.messages += 1
                    self.agent.counter += 1

    class send_value(OneShotBehaviour):
        async def run(self):
            s = self.agent.value
            n = 1
            for i in self.agent.childs_values:
                s += int(i[0])
                n += int(i[1])
            if (self.agent.leader):
                print(f"Average sum is {s/n}")
                await self.agent.stop()

            else:
                msg = Message(to=self.agent.parent_jid + "@" + XMPP_server)
                msg.set_metadata("action", "send_value")
                msg.body = f"{s},{n}"
                await self.send(msg)
                self.agent.messages += 1
            self.kill()

    class on_send_value(CyclicBehaviour):
        async def run(self):
            msg = None
            if (self.agent.childs):
                msg = await self.receive(timeout=10)
            if (msg):
                s = msg.body.split(',')[0]
                n = msg.body.split(',')[1]
                self.agent.childs_values.append((s, n))
            if (len(self.agent.childs)==len(self.agent.childs_values)):
                self.agent.add_behaviour(self.agent.send_value())
                self.kill()

    class on_make_child_answer(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if (msg):
                answer = msg.body
                if (answer):
                    self.agent.childs.append(str(msg.sender).split("@")[0])
                    b = self.agent.on_send_value()
                    if (not self.agent.has_on_send_value_behaviour):
                        t = Template()
                        t.set_metadata("action", "send_value")
                        self.agent.add_behaviour(b, t)
                        self.agent.has_on_send_value_behaviour = True
                self.agent.counter -=1
            if (self.agent.counter == 0):
                if (not self.agent.childs):
                    self.agent.add_behaviour(self.agent.send_value())
                self.kill()

    async def setup(self):
        b = self.on_make_child_reply()
        t = Template()
        t.set_metadata("action", "make_child")
        self.add_behaviour(b, t)
        if (self.leader):    
            self.add_behaviour(self.send_make_child())
        
        t = Template()
        t.set_metadata("action", "answer")
        self.add_behaviour(self.on_make_child_answer(), t)
        
    
graph = [
        [f"agent{i}" for i in [1, 2, 4, 3, 17]],
        [f"agent{i}" for i in [0, 18]],       
        [f"agent{i}" for i in [0, 6]],
        [f"agent{i}" for i in [0, 17]],
        [f"agent{i}" for i in [0, 5, 9]],
        [f"agent{i}" for i in [4]],
        [f"agent{i}" for i in [2, 7]],
        [f"agent{i}" for i in [6, 9, 8]],
        [f"agent{i}" for i in [7]],
        [f"agent{i}" for i in [4, 7, 10]], 
        [f"agent{i}" for i in [9, 11]],
        [f"agent{i}" for i in [10]],
        [f"agent{i}" for i in [3, 13, 14]],
        [f"agent{i}" for i in [12]],
        [f"agent{i}" for i in [12, 15, 17]],
        [f"agent{i}" for i in [14, 17]],
        [f"agent{i}" for i in [17]],
        [f"agent{i}" for i in [14, 15,0, 16, 18]],
        [f"agent{i}" for i in [17, 1]],
        ]

if __name__ == "__main__":
    s = 0
    for i in range(1, len(graph)):
        val = randint(0, 1000)
        s += val
        MyAgent(graph[i], False, val, f"agent{i}@{XMPP_server}", "mypass", verify_security=False).start().result()
    
    print(f"True average value is {s/len(graph)}")
    leader = MyAgent(graph[0], True, 0, f"agent{0}@{XMPP_server}", "mypass", verify_security=False)
    leader.start().result()
    
    while leader.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
    quit_spade()
    print("Agents finished")
