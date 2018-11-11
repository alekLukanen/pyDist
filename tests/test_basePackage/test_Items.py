
from pyDist import Items


def test_create_cluster_item():
    cluster_item = Items.ClusterItem()
    assert cluster_item


def test_pop_tracer_from_empty():
    cluster_item = Items.ClusterItem()
    assert cluster_item.pop_tracer() is None


def test_pop_tracer_from_non_empty_1():
    cluster_item = Items.ClusterItem()
    assert not cluster_item.in_cluster_network()
    cluster_item.add_trace('N1')
    assert not cluster_item.in_cluster_network()
    assert cluster_item.pop_tracer() == 'N1'
    assert cluster_item.pop_tracer() is None
    assert not cluster_item.in_cluster_network()
    assert cluster_item.trace() == ['N1']


def test_pop_tracer_from_non_empty_2():
    cluster_item = Items.ClusterItem()
    assert not cluster_item.in_cluster_network()
    cluster_item.add_trace('N1')
    assert not cluster_item.in_cluster_network()
    cluster_item.add_trace('N2')
    assert cluster_item.in_cluster_network()
    assert cluster_item.pop_tracer() == 'N2'
    assert cluster_item.pop_tracer() == 'N1'
    assert cluster_item.pop_tracer() is None
    assert not cluster_item.in_cluster_network()
    assert cluster_item.trace() == ['N1', 'N2']


def test_pop_tracer_from_non_empty_3():
    cluster_item = Items.ClusterItem()
    assert not cluster_item.in_cluster_network()
    cluster_item.add_trace('N1')
    assert not cluster_item.in_cluster_network()
    cluster_item.add_trace('N2')
    assert cluster_item.in_cluster_network()
    cluster_item.add_trace('N3')
    assert cluster_item.in_cluster_network()
    assert cluster_item.pop_tracer() == 'N3'
    assert cluster_item.pop_tracer() == 'N2'
    assert cluster_item.pop_tracer() == 'N1'
    assert cluster_item.pop_tracer() is None
    assert not cluster_item.in_cluster_network()
    assert cluster_item.trace() == ['N1', 'N2', 'N3']

