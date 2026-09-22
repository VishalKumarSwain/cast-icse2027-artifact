import os

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
SUDOKUS_PATH = os.path.join(SCRIPT_PATH, "..", "sudokus")
TESTS_PATH = os.path.join(SCRIPT_PATH, "..", "..", "java", "sudoku")
TESTFILE_PATH = os.path.join(TESTS_PATH, "TestSolve.java")

INTROTEXT = """package sudoku;

import static org.junit.jupiter.api.Assertions.*;
import org.opentest4j.AssertionFailedError;
import org.junit.jupiter.api.*;

class TestSolve {
    Solver s;

    @BeforeEach
    void setUp() {
        s = Solver.ofDefaults();
    }

    @AfterEach
    void tearDown() {
        s = null;
    }
"""

with open(TESTFILE_PATH, "w") as outfile:
    outfile.write(INTROTEXT)
    for sudoku in os.listdir(SUDOKUS_PATH):
        sudokufile_path = os.path.join(SUDOKUS_PATH, sudoku)
        with open(sudokufile_path, "r") as infile:
            outfile.write("\n\n    @Test\n    void testSolve" + sudoku[:-4] + "() { ")
            for r, line in enumerate(infile.readlines()):
                nums = line.split(" ")[:-1]
                for c, num in enumerate(nums):
                    outfile.write(f"\n        s.setOrClearNumber({r}, {c}, {num});")
            outfile.write("\n        s.solve();")
            outfile.write("\n        assertTrue(s.isAllValid());")
        outfile.write("\n    }")
    outfile.write("\n}")
