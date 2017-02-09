class EFcalculator(object):

    # converts wosids to ints
    # and accumulates necessary statistics
    def __init__(self):
        # set of w^s is keys of foo_w
        self.set_ws = set()
        # w^s -> w^i (wos id str to wos id int)
        self.foo_w = {}
        # w^i -> j^i (wos id int to journal int)
        self.foo_wj = {}
        # citation dict:
        # w^i_a -> w^i_b (citations wos_id to wos_ids)
        self.foo_cite = {}

    def update_foo_w(self, new_wosids_set):
        new_wosids = new_wosids_set - self.set_ws
        n = len(self.set_ws)
        foo_w_iter = dict(zip(list(new_wosids),
                          range(n, n+len(new_wosids))))
        self.set_ws |= new_wosids
        self.foo_w.update(foo_w_iter)

    def update_foo_wj(self, foo_wj_incoming):
        if type(foo_wj_incoming) == dict:
            foo_wj_iter = {self.foo_w[k]: v for k, v
                           in foo_wj_incoming.iteritems()}
        elif type(foo_wj_incoming) in (list, tuple):
            foo_wj_iter = {self.foo_w[x[0]]: x[1] for x in foo_wj_incoming}
        self.foo_wj.update(foo_wj_iter)
        print(len(self.foo_wj.keys()))

    def update_foo_ab(self, acc):

        foo_cite_iter = {self.foo_w[x[0]]:
                         [self.foo_w[y] for y in x[1]] for x in acc}
        self.foo_cite.update(foo_cite_iter)

    def update_with_citations_tuple(self, acc, fill_ab=False):
        """

        :param acc: (wosid(str), issn(int), [ref(str)])
        :param fill_ab:
        :return:
        """
        new_set_ws = set(map(lambda x: x[0], acc))

        self.update_foo_w(new_set_ws)
        wj = map(lambda x: (x[0], x[1]), acc)
        self.update_foo_wj(wj)
        if fill_ab:
            new_set_ws = set(x for ll in map(lambda x: x[2], acc) for x in ll)
            self.update_foo_w(new_set_ws)
            cite_tmp = map(lambda x: (x[0], x[2]), acc)
            self.update_foo_ab(cite_tmp)

    def update(self, foo_wj_iter):
        self.foo_wj.update(foo_wj_iter)

