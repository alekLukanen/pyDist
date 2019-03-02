import pyDist

from pyDist import Interfaces, exSheet


def test(a):
    return a+1


if __name__ == '__main__':

    ip = '127.0.0.1'
    port = 9000
    a = 100
    with Interfaces.ClusterExecutor(ip, port) as cluster:

        cluster.connect(f'rusty', group_id='rust_group')
        _ = cluster.submit(test, a)

        for f in cluster.as_completed():
            print(f'result: {f.result()}')

        cluster.disconnect()
        cluster.shutdown_executor()
    print('done!')
