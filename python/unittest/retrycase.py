import sys
import unittest
import warnings
from unittest import result
from unittest.case import _ExpectedFailure, _UnexpectedSuccess, SkipTest

class RetryTestCase(unittest.TestCase):
    """gives every failing test a second chance

    we have a large Set of Selenium2-WebDriver tests written with python and test by nose.
    Due to a very aggressive timing (only short wait periods after the clicks)
    some tests (1 out of 100, and always a different one) can fail because the server
    sometimes responds a bit slower.
    But we can not make the wait period so long that it is definitely long enough,
    because then the tests will take for ever.)
    -- So I think it is acceptable for this use case that a test is green even if it needs a second try.
    this class support for a 2 out of 3 majority:
         --(repeat a failing test 3 times, and take them as correct, if two of the tests are correct)
    """

    def __init__(self, methodName='runTest'):
        self.retry_count = 2
        self._result = result.TestResult()
        super(RetryTestCase, self).__init__(methodName)

    def run(self, result=None):
        while self.retry_count > 0:
            self.retry_count = self.retry_count - 1
            orig_result = result
            if result is None:
                result = self.defaultTestResult()
                startTestRun = getattr(result, 'startTestRun', None)
                if startTestRun is not None:
                    startTestRun()

            self._resultForDoCleanups = result
            result.startTest(self)

            testMethod = getattr(self, self._testMethodName)
            if (getattr(self.__class__, "__unittest_skip__", False) or
                getattr(testMethod, "__unittest_skip__", False)):
                # If the class or method was skipped.
                try:
                    skip_why = (getattr(self.__class__, '__unittest_skip_why__', '')
                                or getattr(testMethod, '__unittest_skip_why__', ''))
                    self._addSkip(result, skip_why)
                finally:
                    result.stopTest(self)
                return
            try:
                success = False
                try:
                    self.setUp()
                except SkipTest as e:
                    self._addSkip(result, str(e))
                except KeyboardInterrupt:
                    raise
                except:
                    if self.retry_count == 0:
                        result.addError(self, sys.exc_info())
                else:
                    try:
                        testMethod()
                    except KeyboardInterrupt:
                        raise
                    except self.failureException:
                        if self.retry_count == 0:
                            result.addFailure(self, sys.exc_info())
                    except _ExpectedFailure as e:
                        addExpectedFailure = getattr(result, 'addExpectedFailure', None)
                        if addExpectedFailure is not None:
                            addExpectedFailure(self, e.exc_info)
                        else:
                            warnings.warn("TestResult has no addExpectedFailure method, reporting as passes",
                                          RuntimeWarning)
                            result.addSuccess(self)
                    except _UnexpectedSuccess:
                        addUnexpectedSuccess = getattr(result, 'addUnexpectedSuccess', None)
                        if addUnexpectedSuccess is not None:
                            addUnexpectedSuccess(self)
                        else:
                            warnings.warn("TestResult has no addUnexpectedSuccess method, reporting as failures",
                                          RuntimeWarning)
                            if self.retry_count == 0:
                                result.addFailure(self, sys.exc_info())
                    except SkipTest as e:
                        self._addSkip(result, str(e))
                    except:
                        if self.retry_count == 0:
                            result.addError(self, sys.exc_info())
                    else:
                        success = True

                    try:
                        self.tearDown()
                    except KeyboardInterrupt:
                        raise
                    except:
                        if self.retry_count == 0:
                            result.addError(self, sys.exc_info())
                        success = False

                cleanUpSuccess = self.doCleanups()
                success = success and cleanUpSuccess
                if success:
                    result.addSuccess(self)
                    return
            finally:
                result.stopTest(self)
                if orig_result is None:
                    stopTestRun = getattr(result, 'stopTestRun', None)
                    if stopTestRun is not None:
                        stopTestRun()
