from modules.Module import Module
import re
import random

class Game(Module):
    def __init__(self, db):
        super().__init__("Game")
        self.commands = [
            ("hodge podge roll a d\d+\s*$", self.roll),
            ("hodge podge give .* \d+ .* points?\s*$", self.editPoints),
            ("hodge podge take \d+ .* points? from .*\s*$", self.editPoints),
            ("hodge podge list all score types\s*$", self.listPoints),
            ("hodge podge summerise .* points?\s*$", self.getPoints)
        ]
        self.db = db
        self.scoreEditLevel = 0

    def roll(self, message, level):
        s = re.search(r"hodge podge roll a d(\d+)\s*$",message.content)
        d = int(s.group(1))
        res = super().blankRes()
        if d > 1000:
            res["output"].append("Sorry friend! That number is too big")
        else:
            roll = str(random.randint(1,d))
            res["output"].append("It landed on "+roll+"!")
        return res

    def editPoints(self, message, level):
        if level < self.scoreEditLevel:
            return

        s1 = re.search(r"hodge podge give (.*) (\d+) (.*) points?\s*$",message.content)
        s2 = re.search(r"hodge podge take (\d+) (.*) points? from (.*)\s*$",message.content)

        if s1:
            s = s1
            score = int(s.group(2))
            scoreType = self.shallowClean(s.group(3))
        elif s2:
            s = s2
            score = int(s.group(1))*-1
            scoreType = self.shallowClean(s.group(2))

        person = None
        if len(message.mentions) != None:
            person = message.mentions[0].name
        res = super().blankRes()

        if not person:
            res["output"].append("Sorry! I don't know who to target! Did you make sure to use a valid `@` mention?")
        else:
            new = self.db.scoreEdit(message.channel.id, scoreType, person, score)
            res["output"].append(person + " now has "+str(new)+" points!")
        return res

    def listPoints(self, message, level):
        if level < self.scoreEditLevel:
            return
        l = self.db.scoreListTypes(message.channel.id)
        res = super().blankRes()
        result = []
        if len(l) == 0:
            result.append("I'm not keeping track of any points yet!")
        else:
            result.append("Here's all the score types i'm keeping track off!")
            for line in l:
                result.append(":::> **"+line+"**")
        res["output"].append("\n".join(result))
        return res

    def getPoints(self, message, level):
        if level < self.scoreEditLevel:
            return

        s = re.search("hodge podge summerise (.*) points\s*$",message.content)
        scoreType = self.shallowClean(s.group(1))
        l = self.db.getAllScores(message.channel.id, scoreType)
        res = super().blankRes()
        result = []
        if len(l) == 0:
            result.append("Nobody has any points yet!")
        else:
            result.append("Here's all the "+scoreType+"scores!")
            for line in l:
                result.append(":::> **"+line[0]+"** : "+line[1])
        res["output"].append("\n".join(result))
        return res

    def shallowClean(self, t):
        return t.strip().lower()

    def clean(self, t):
        m = t.lower()
        m = re.sub(r'\s+',' ',m)
        m = re.sub(r'[\,\.\?\;\:\%\#\@\!\^\&\*\+\-\+\_\~\']','',m)
        m = m.strip()
        return m

    def trigger(self, message, requestLevel):
        res = super().blankRes()
        original = message.content;
        m = self.clean(message.content)
        for command in self.commands:
            if re.search(command[0],m):
                res = command[1](message,requestLevel)
        return res