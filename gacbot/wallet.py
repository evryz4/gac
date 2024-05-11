from hashlib import sha256
from time import time
import json
import os

class Block:
    def __init__(self, data):
        self.data = data
        self.timestamp = time()
        self.hash = None
        self.prevhash = None
        self.updhash()
    
    def updhash(self):
        self.hash = sha256()
        self.hash.update(str(self.prevhash).encode())
        self.hash.update(str(self.timestamp).encode())
        self.hash.update(str(self.data).encode())

        self.hash = self.hash.hexdigest()

class Chain:
    def __init__(self):
        self.chain = []
        self.chain.append(Block(None))
    
    def last(self):
        return self.chain[-1]

    def addblock(self, block: Block):
        block.prevhash = self.last().hash
        block.updhash()

        self.chain.append(block)
    
    def __repr__(self):
        return json.dumps([{'data': i.data, 'timestamp': i.timestamp, 'hash': i.hash, 'prevhash': str(i.prevhash)} for i in self.chain], indent=4)

class Coin:
    def __init__(self, file: str):
        self.chain = Chain()
        self.file = file
        if os.path.exists(self.file):
            self.chain.chain = []
            with open(self.file) as file:
                content = file.read()
            for i in json.loads(content):
                block = Block(data=i['data'])
                block.timestamp = i['timestamp']
                block.hash = i['hash']
                block.prevhash = i['prevhash']
                self.chain.chain.append(block)
    
    def save(self):
        with open(self.file, 'w') as file:
            file.write(str(self.chain))
    
    def setemission(self, *, amount: int):
        self.chain.addblock(Block({'from': None, 'to': 'EMISSION', 'amount': amount, 'comment': 'set emission'}))
        self.save()

    def emission(self, *, to, amount: int, comment: str | None = None):
        self.transfer(fromh='EMISSION', to=to, amount=amount, comment=comment)
    
    def transfer(self, *, fromh, to, amount: int, comment: str | None = None) -> bool:
        if self.getholders()[fromh] >= amount:
            self.chain.addblock(Block({'from': fromh, 'to': to, 'amount': amount, 'comment': comment}))
            self.save()
        return self.getholders()[fromh] >= amount

    def getholders(self):
        ret = {}
        for i in self.chain.chain[1:]:
            amount = i.data['amount']

            if i.data['to'] in ret:
                ret[i.data['to']] += amount
            else:
                ret[i.data['to']] = amount

            if i.data['from'] in ret:
                ret[i.data['from']] -= amount
            else:
                ret[i.data['from']] = -amount
        
        return ret
    
    def __repr__(self):
        return str(self.chain)