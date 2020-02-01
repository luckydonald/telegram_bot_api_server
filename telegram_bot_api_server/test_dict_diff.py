import difflib
import unittest
from enum import IntFlag, auto
from typing import List, Tuple, Optional, Dict, Any, Callable


class DictDiffer(object):

    def __init__(self, a, b,
        route: str = "",
        volatile_fields: Optional[List[str]] = None,
        optional_fields: Optional[List[str]] = None,
        additional_fields: Optional[List[str]] = None,
    ):
        self.route = route
        self.volatile_fields = self._prepare_fields(route, volatile_fields)
        self.optional_fields = self._prepare_fields(route, optional_fields)
        self.additional_fields = self._prepare_fields(route, additional_fields)
        self.a = a
        self.b = b
    # end def

    def format_dict_line(self, key: str, value: List):
        result = [f'{key!r}: {value[0]}']
        if len(value) == 1:
            return result
        else:
            return [f'{key!r}: {value[0]}']

    class Status(IntFlag):
        def __bool__(self) -> bool:
            return not super().__bool__()
        # end def

        SUCCESS = 0
        FAIL_DIFFERENT = auto()
        FAIL_MISSING = auto()
        FAIL_EXTRA = auto()
    # end class

    def print(self) -> Status:
        success, text = self.to_string()
        print(text)
        return success
    # end def

    def to_string(self) -> Tuple[Status, str]:
        success, lines_a, lines_b = self.render()
        return success, self.create_diff(lines_a, lines_b)
    # end def

    @staticmethod
    def create_diff(lines_a, lines_b):
        return '\n'.join(difflib.ndiff(lines_a, lines_b))
    # end def

    def render(self) -> Tuple[Status, List[str], List[str]]:
        """
        :return: (success, lines_a, lines_b)
        """
        if isinstance(self.a, dict):
            assert isinstance(self.b, dict)
            return self.render_dict()
        elif isinstance(self.a, list):
            assert isinstance(self.b, list)
            return self.render_list()
        elif isinstance(self.a, (int, bool, float, str)):
            assert isinstance(self.b, (int, bool, float, str))
            return self.Status.SUCCESS if self.a == self.b else self.Status.FAIL_DIFFERENT, [repr(self.a)], [repr(self.b)]
        else:
            raise TypeError('Not supported.')
        # end if
    # end def

    def render_list(self) -> Tuple[Status, List[str], List[str]]:
        """
        :return: (is_wrong, lines_a, lines_b)
        """
        result_a: List[str] = ['[']  # start the dict
        result_b: List[str] = ['[']  # start the dict

        i_a: int = 0  # used to calulate missing fields
        i_b: int = 0  # used to calulate missing fields
        i: int = 0

        is_wrong: DictDiffer.Status = self.Status.SUCCESS

        len_a = len(self.a)
        len_b = len(self.b)

        if len_a > len_b:
            is_wrong |= self.Status.FAIL_MISSING
        # end if
        if len_a < len_b:
            is_wrong |= self.Status.FAIL_EXTRA
        # end if

        while True:
            key_route = f'{self.route}{i!s}'  # remember to add '.' when calling recursive.
            value_a = self.a[i_a]
            value_b = self.b[i_b]

            # no success => this list is somehow different.
            success, list_a, list_b = DictDiffer(value_a, value_b, route=key_route + '.', volatile_fields=self.volatile_fields, optional_fields=self.optional_fields, additional_fields=self.additional_fields).render()

            volatile_field_saved_the_day = False
            if not success:
                if key_route in self.volatile_fields:
                     volatile_field_saved_the_day = True
                else:
                    is_wrong |= self.Status.FAIL_DIFFERENT
                # end if
            # end if

            def add_multiline(
                result_x: List[str], list_x: List[str], volatile_field_saved_the_day: bool
            ) -> List[str]:
                """modifies the list to have the needed elements"""
                assert len(list_x) > 1  # we need to handle this: Single line values like `True` or `123`.

                # first, make the current line, like `"asd": {`.
                # also if there is an error inside, but we are marked volatile, we can ignore that.
                if volatile_field_saved_the_day:
                    result_x.append(f'  {list_x[0]}  # volatile field')
                else:
                    result_x.append(f'  {list_x[0]}')
                # end if

                # add all lines in the middle, adding spaces for indention.
                # the loops will not run if we have less than 3 elements,
                # i.e. nothing between first and last line.
                for elem in list_x[1:-1]:
                    result_x.append(f'  {elem}')
                # end for

                # now if we have a last element we add that, and the closing komma, like `},`
                if len(list_x) > 1:
                    result_x.append(f'  {list_x[-1]},')
                # end if
                return result_x

            # end def

            result_a = add_multiline(result_a, list_a, volatile_field_saved_the_day)
            result_b = add_multiline(result_b, list_b, volatile_field_saved_the_day)

            i += 1
            if i >= len_a or i >= len_b:
                break
            # end if
        # end while

        result_a.append(']')  # close the list
        result_b.append(']')  # close the list
        return is_wrong, result_a, result_b
    # end def


    def render_dict(self) -> Tuple[Status, List[str], List[str]]:
        """
        :return: (is_wrong, lines_a, lines_b)
        """
        result_a: List[str] = ['{']  # start the dict
        result_b: List[str] = ['{']  # start the dict

        keys = list(set(list(self.a.keys()) + list(self.b.keys())))
        keys.sort()

        is_wrong: DictDiffer.Status = self.Status.SUCCESS

        for key in keys:
            key_route = f'{self.route}{key}'  # remember to add '.' when calling recursive.
            if key in self.a:
                if key in self.b:
                    # a and b have the key
                    # => we need to handle them being equal or in `self.volatile_fields`, i.e. that changed values are okey.
                    value_a = self.a[key]
                    value_b = self.b[key]
                    success, list_a, list_b = DictDiffer(value_a, value_b, route=key_route + '.', volatile_fields=self.volatile_fields, optional_fields=self.optional_fields, additional_fields=self.additional_fields).render()
                    volatile_field_saved_the_day = not success and key_route in self.volatile_fields
                    if not success and not volatile_field_saved_the_day:
                        is_wrong |= self.Status.FAIL_DIFFERENT
                    # end if

                    assert len(list_a) > 0
                    assert len(list_b) > 0
                    if len(list_a) == 1 and len(list_b) == 1:
                        # both are the single line, so it will just diff this line.
                        # |=| - "asd": 1,
                        # |=| + "asd": 2,

                        # no need to check `self.volatile_fields`, they are okey anyway.
                        # if they are not the same, we check if we have to add a note
                        if volatile_field_saved_the_day:  # the `and` can be read as `but`.
                            # it failed, but that is allowed
                            result_a.append(f'  {key!r}: {list_a[0]},  # volatile')
                            result_b.append(f'  {key!r}: {list_b[0]},  # volatile')
                        else:
                            result_a.append(f'  {key!r}: {list_a[0]},')
                            result_b.append(f'  {key!r}: {list_b[0]},')
                        # end if
                    else:
                        # if any of those is not a single line, make it multiline,
                        # to make comparing easier, even with empty elements.
                        # |=|   "asd": {
                        # |=| +   "sample": "text",
                        # |=|   },

                        def add_multiline(
                            key: str, result_x: List[str], list_x: List[str], volatile_field_saved_the_day: bool
                        ) -> List[str]:
                            """modifies the list to have the needed elements"""
                            assert len(list_x) > 1  # we need to handle this: Single line values like `True` or `123`.

                            # first, make the current line, like `"asd": {`.
                            # also if there is an error inside, but we are marked volatile, we can ignore that.
                            if volatile_field_saved_the_day:
                                result_x.append(f'  {key!r}: {list_x[0]}  # volatile field')
                            else:
                                result_x.append(f'  {key!r}: {list_x[0]}')
                            # end if

                            # add all lines in the middle, adding spaces for indention.
                            # the loops will not run if we have less than 3 elements,
                            # i.e. nothing between first and last line.
                            for elem in list_x[1:-1]:
                                result_x.append(f'  {elem}')
                            # end for

                            # now if we have a last element we add that, and the closing komma, like `},`
                            if len(list_x) > 1:
                                result_x.append(f'  {list_x[-1]},')
                            # end if
                            return result_x
                        # end def

                        result_a = add_multiline(key, result_a, list_a, volatile_field_saved_the_day)
                        result_b = add_multiline(key, result_b, list_b, volatile_field_saved_the_day)

                        # basically all is fine if either the field is volatile or correct.
                        # otherwise we need to inherit that status
                        is_wrong |= self.Status.SUCCESS if volatile_field_saved_the_day or success else self.Status.FAIL_DIFFERENT
                    # end if
                else:  # only `self.a` has the key
                    # we expected a key, but it's not there
                    # is the key optional?

                    # faking a diff here, to get the print output...
                    value_a = self.a[key]
                    success, list_a, _ = DictDiffer(value_a, value_a, route=key_route + '.', volatile_fields=self.volatile_fields, optional_fields=self.optional_fields, additional_fields=self.additional_fields).render()
                    assert success  # as it is diffing two times the exactly same stuff.
                    if key_route in self.optional_fields:  # so all is okey.
                        result_a.append(f'  {key!r}: {list_a[0]}  # optional field')
                    else:
                        result_a.append(f'  {key!r}: {list_a[0]}')
                        is_wrong |= self.Status.FAIL_MISSING
                    # end if

                    # add all lines in the middle, adding spaces for indention.
                    # the loops will not run if we have less than 3 elements,
                    # i.e. nothing between first and last line.
                    for elem in list_a[1:-1]:
                        result_a.append(f'  {elem}')
                    # end for

                    # now if we have a last element we add that, and the closing komma, like `},`
                    if len(list_a) > 1:
                        result_a.append(f'  {list_a[-1]},')
                    # end if
                # end if
            else:  # `self.a` has no key
                if key in self.b:  # only `self.b` has a key
                    # we expected no key, but it could happen
                    # is the key additional?

                    # faking a diff here, to get the print output...
                    value_b = self.b[key]
                    success, _, list_b = DictDiffer(value_b, value_b, route=key_route + '.', volatile_fields=self.volatile_fields, optional_fields=self.optional_fields, additional_fields=self.additional_fields).render()
                    assert success  # as it is diffing two times the exactly same stuff.
                    if key_route in self.additional_fields:  # so all is okey.
                        result_b.append(f'  {key!r}: {list_b[0]}  # additional field')
                    else:
                        result_b.append(f'  {key!r}: {list_b[0]}')
                        is_wrong |= self.Status.FAIL_EXTRA
                    # end if

                    # add all lines in the middle, adding spaces for indention.
                    # the loops will not run if we have less than 3 elements,
                    # i.e. nothing between first and last line.
                    for elem in list_b[1:-1]:
                        result_b.append(f'  {elem}')
                    # end for

                    # now if we have a last element we add that, and the closing komma, like `},`
                    if len(list_b) > 1:
                        result_b.append(f'  {list_b[-1]},')
                    # end if
                else:
                    # the key is no where to be found?!?
                    raise ArithmeticError('Wait what. We made a list combining the keys of the dicts, and now that key was not found?!?')
                # end if
            # end if
        # end for

        result_a.append('}')  # close the dict
        result_b.append('}')  # close the dict
        return is_wrong, result_a, result_b
    # end def

    @staticmethod
    def _prepare_fields(route: str, fields: Optional[List[str]]) -> List[str]:
        new_fields = []
        if fields:
            for field in fields:
                if not field.startswith(route):
                    continue  # don't append => ignore
                # end if
                new_fields.append(field)
            # end for
        # end if
        return new_fields
    # end if

    @classmethod
    def unittest_compare(
        cls,
    ) -> Callable[
        [
            Any,
            Dict[str, Any],
            Dict[str, Any],
            Optional[str],
            Optional[List[str]],
            Optional[List[str]],
            Optional[List[str]],
            bool,
        ],
        None,
    ]:
        def unittest_compare_inner(
            unittest_self: Any,
            expected: Dict[str, Any],
            result: Dict[str, Any],
            msg: Optional[str] = 'real one vs generated one',
            volatile_fields: Optional[List[str]] = None,
            optional_fields: Optional[List[str]] = None,
            additional_fields: Optional[List[str]] = None,
            print_correct: bool = True,
        ):
            """
            Checks whether dictionary is a equal, while allowing to specify fields to skip.

            Format of `volatile_fields`, `optional_fields` and `additional_fields`:
            Using the key of the field. E.g. `volatile_fields=['date']` with an dict like `{'important': 'text', 'date': 1580479629}`

            :param expected: Input what we want to have,
            :param result: What we got instead
            :param msg: Provide some insights what is failing.
            :param volatile_fields: A list of fields which needs to be there, but can be any value. See format above.
            :param optional_fields: A list of fields which doesn't need to be there, which are allowed to be missing in `result`. See format above.
            :param additional_fields: A list of fields which are allowed to be here regardless of them not being specified in `expected`. See format above.
            :param print_correct: If it should be printed if it is correct.
            """
            status, lines_a, lines_b = cls(
                a=expected, b=result,
                volatile_fields=volatile_fields, optional_fields=optional_fields, additional_fields=additional_fields
            ).render()

            if status:
                # everything is fine
                if print_correct:
                    print(DictDiffer.create_diff(lines_a, lines_b))
                return
            # end if

            try:
                from teamcity import is_running_under_teamcity
                from teamcity.diff_tools import EqualsAssertionError
            except ImportError:
                is_running_under_teamcity = lambda: False
            # end if

            msg = unittest_self._formatMessage(msg, 'advanced comparison resulted in a failure.'),

            if is_running_under_teamcity():
                error = EqualsAssertionError("\n".join(lines_a), "\n".join(lines_b), msg)
                assert error.can_be_serialized()
                raise error
            # end if

            # else-fallback:
            unittest_self.assertEqual(status, DictDiffer.Status.SUCCESS, msg=DictDiffer.create_diff(lines_a, lines_b) + '\n' + msg)
        # end def
        return unittest_compare_inner
    # end def
# end class


class DictDifferSimpleTestCase(unittest.TestCase):
    def test_same(self):
        diff = DictDiffer({'a': 'abc', 'b': 'abc'}, {'a': 'abc', 'b': 'abc'})
        success = diff.print()
        self.assertTrue(success)
    # end def

    def test_fail_diff(self):
        diff = DictDiffer({'a': 'abc', 'b': 'abc'}, {'a': 'xyz', 'b': 'abc'})
        success = diff.print()
        self.assertEqual(success, DictDiffer.Status.FAIL_DIFFERENT)
    # end def

    def test_fail_missing(self):
        diff = DictDiffer({'a': 'abc', 'b': 'abc'}, {'a': 'abc'})
        success = diff.print()
        self.assertEqual(success, DictDiffer.Status.FAIL_MISSING)
    # end def

    def test_fail_extra(self):
        diff = DictDiffer({'a': 'abc', 'b': 'abc'}, {'a': 'abc', 'b': 'abc', 'c': 'abc'})
        success = diff.print()
        self.assertEqual(success, DictDiffer.Status.FAIL_EXTRA)
    # end def

    def test_allowed_diff(self):
        diff = DictDiffer({'a': 'abc', 'b': 'abc'}, {'a': 'xyz', 'b': 'abc'}, volatile_fields=['a'])
        success = diff.print()
        self.assertEqual(success, DictDiffer.Status.SUCCESS)
    # end def

    def test_allowed_missing(self):
        diff = DictDiffer({'a': 'abc', 'b': 'abc'}, {'a': 'abc'}, optional_fields=['b'])
        success = diff.print()
        self.assertEqual(success, DictDiffer.Status.SUCCESS)
    # end def

    def test_allowed_extra(self):
        diff = DictDiffer({'a': 'abc', 'b': 'abc'}, {'a': 'abc', 'b': 'abc', 'c': 'abc'}, additional_fields=['c'])
        success = diff.print()
        self.assertEqual(success, DictDiffer.Status.SUCCESS)
    # end def
# end class




class DictDifferNestedTestCase(unittest.TestCase):
    def test_same(self):
        diff = DictDiffer(
            {'a': {'b': {'c': 'abc', 'd': 'abc', 'e': 'abc'}}},
            {'a': {'b': {'c': 'abc', 'd': 'abc', 'e': 'abc'}}}
        )
        success = diff.print()
        self.assertTrue(success)
    # end def

    def test_fail_diff(self):
        diff = DictDiffer(
            {'a': {'b': {'c': 'abc', 'd': 'abc', 'e': 'abc'}}},
            {'a': {'b': {'c': 'abc', 'd': 'xyz', 'e': 'abc'}}}
        )
        success = diff.print()
        self.assertEqual(success, DictDiffer.Status.FAIL_DIFFERENT)
    # end def

    def test_fail_missing(self):
        diff = DictDiffer(
            {'a': {'b': {'c': 'abc', 'd': 'abc', 'e': 'abc'}}},
            {'a': {'b': {'c': 'abc', 'e': 'abc'}}}
        )
        success = diff.print()
        self.assertEqual(success, DictDiffer.Status.FAIL_DIFFERENT)
    # end def

    def test_fail_extra(self):
        diff = DictDiffer(
            {'a': {'b': {'c': 'abc', 'd': 'abc', 'e': 'abc'}}},
            {'a': {'b': {'c': 'abc', 'd': 'abc', 'e': 'abc', 'z': 'extra'}}}
        )
        success = diff.print()
        self.assertEqual(success, DictDiffer.Status.FAIL_DIFFERENT)
    # end def

    def test_allowed_diff(self):
        diff = DictDiffer(
            {'a': {'b': {'c': 'abc', 'd': 'abc', 'e': 'abc'}}},
            {'a': {'b': {'c': 'abc', 'd': 'xyz', 'e': 'abc'}}},
            volatile_fields=['a.b.d']
        )
        success = diff.print()
        self.assertEqual(success, DictDiffer.Status.SUCCESS)
    # end def

    def test_allowed_missing(self):
        diff = DictDiffer(
            {'a': {'b': {'c': 'abc', 'd': 'abc', 'e': 'abc'}}},
            {'a': {'b': {'c': 'abc', 'e': 'abc'}}},
            optional_fields=['a.b.e']
        )
        success = diff.print()
        self.assertEqual(success, DictDiffer.Status.SUCCESS)
    # end def

    def test_allowed_extra(self):
        diff = DictDiffer(
            {'a': {'b': {'c': 'abc', 'd': 'abc', 'e': 'abc'}}},
            {'a': {'b': {'c': 'abc', 'd': 'abc', 'e': 'abc', 'z': 'extra'}}},
            additional_fields=['a.b.z']
        )
        success = diff.print()
        self.assertEqual(success, DictDiffer.Status.SUCCESS)
    # end def
# end class


if __name__ == '__main__':
    unittest.main()
# end if
