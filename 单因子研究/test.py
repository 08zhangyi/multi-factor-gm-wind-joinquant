class A(object):
    def __getitem__(self, item):
        print(item)

a = A()
a[4]