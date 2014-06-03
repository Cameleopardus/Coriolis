from multiprocessing import Pool, cpu_count


WORKER_THREADCOUNT = cpu_count() + 1


class Worker():
    pool = Pool(WORKER_THREADCOUNT)

    def do_work(self, f, args=None, async=True, pipe=None):
        #add to pool
        if pipe is not None:
            r = self.pool.apply_async(f, args=args)
            pipe.send(r)
        else:
            return self.pool.apply_async(f, args=args)


    def close(self):
        self.pool.close()
        self.pool.terminate()
        self.pool.join()


def welcome():
    print "DEBUG: worker instantiated."
    return "returned!"


def init():
    dbg = Worker().do_work(welcome())
    del dbg
    return Worker()
    pass

