import pytest

from boltons.dictutils import OneToOne


@pytest.mark.parametrize('inverse', [False, True])
@pytest.mark.parametrize(
    'make_input',
    [list, tuple, iter, lambda pairs: (pair for pair in pairs)],
    ids=['list', 'tuple', 'iterator', 'generator'],
)
@pytest.mark.parametrize(
    'pairs',
    [
        [],
        [('a', 1)],
        [('a', 1), ('b', 2), ('c', 3)],
        [('a', 1), ('a', 2), ('b', 2)],
    ],
)
def test_one_to_one_update_iterable(pairs, make_input, inverse):
    mapping = OneToOne({'existing': 0})
    target = mapping.inv if inverse else mapping
    expected = target.copy()
    for key, value in pairs:
        expected[key] = value
    expected['extra'] = 4

    assert target.update(make_input(pairs), extra=4) is None

    assert target == expected
    assert target.inv == expected.inv
    assert target.inv.inv is target


def test_one_to_one_update_zip():
    mapping = OneToOne()
    mapping.update(zip(['a', 'b'], [1, 2]))

    assert mapping == {'a': 1, 'b': 2}
    assert mapping.inv == {1: 'a', 2: 'b'}


@pytest.mark.parametrize('invalid_pair', [([], 2), ('b', []), ('b',)])
@pytest.mark.parametrize('make_input', [list, iter])
def test_one_to_one_update_validates_before_mutating(invalid_pair, make_input):
    mapping = OneToOne({'existing': 0})
    pairs = [('a', 1), ('c', 3), invalid_pair]

    with pytest.raises((TypeError, ValueError)):
        mapping.update(make_input(pairs))

    assert mapping == {'existing': 0}
    assert mapping.inv == {0: 'existing'}


def test_one_to_one_update_validates_keywords_before_mutating():
    mapping = OneToOne({'existing': 0})

    with pytest.raises(TypeError):
        mapping.update(iter([('a', 1), ('b', 2)]), invalid=[])

    assert mapping == {'existing': 0}
    assert mapping.inv == {0: 'existing'}


def test_one_to_one_update_failing_iterator():
    def pairs():
        yield 'a', 1
        yield 'b', 2
        raise RuntimeError('iteration failed')

    mapping = OneToOne({'existing': 0})
    with pytest.raises(RuntimeError, match='iteration failed'):
        mapping.update(pairs())

    assert mapping == {'existing': 0}
    assert mapping.inv == {0: 'existing'}
