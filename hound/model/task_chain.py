import Queue
from Queue import PriorityQueue

class TaskChain(object):

    def __init__(self):
        self.task_chain = PriorityQueue()
        self.task_num = 0

    def put(self, task):
        try:
            self.task_chain.put_nowait((self.task_num, task))
            self.task_num += 1
        except Queue.Full as e:
            raise e

    def get(self):
        try:
            priority, task = self.task_chain.get_nowait()
            self.task_num -= 1
            return task
        except Queue.Empty as e:
            raise  e

    def size(self):
        return self.task_num

if __name__ == '__main__':
    chain = TaskChain()

    chain.put('111')
    chain.put('222')

    print chain.get()
    print chain.get()
    print chain.get()
