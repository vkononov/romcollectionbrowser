# -*- coding: utf-8 -*-
import os
import sqlite3
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))

import util


class TestSortOrder(unittest.TestCase):

    def test_sql_uses_article_strip_when_name_and_enabled(self):
        sql = util.sql_game_list_order_by('name', 'ASC', ignore_articles=True)
        self.assertIn('GLOB', sql)
        self.assertIn("ORDER BY", sql)
        self.assertIn('name COLLATE NOCASE ASC', sql)

    def test_sql_plain_when_disabled(self):
        sql = util.sql_game_list_order_by('name', 'DESC', ignore_articles=False)
        self.assertEqual(sql, 'ORDER BY name COLLATE NOCASE DESC')

    def test_sql_other_column_unchanged(self):
        sql = util.sql_game_list_order_by('year', 'ASC', ignore_articles=True)
        self.assertEqual(sql, 'ORDER BY year COLLATE NOCASE ASC')

    def test_sqlite_order_matches_article_ignore(self):
        order_sql = util.sql_game_list_order_by('name', 'ASC', ignore_articles=True)
        con = sqlite3.connect(':memory:')
        con.execute('CREATE TABLE GameView (id INT, name TEXT)')
        rows = [
            (1, 'The Legend of Zelda'),
            (2, 'Battleship'),
            (3, 'A Boy and His Blob'),
            (4, 'Zaxxon'),
            (5, 'An American Tail'),
        ]
        con.executemany('INSERT INTO GameView VALUES (?,?)', rows)
        q = 'SELECT name FROM GameView ' + order_sql
        names = [r[0] for r in con.execute(q).fetchall()]
        con.close()
        # Sort keys: American Tail, Battleship, Boy..., Legend..., Zaxxon
        self.assertEqual(names[0], 'An American Tail')
        self.assertEqual(names[1], 'Battleship')
        self.assertEqual(names[2], 'A Boy and His Blob')
        self.assertEqual(names[3], 'The Legend of Zelda')
        self.assertEqual(names[4], 'Zaxxon')


if __name__ == '__main__':
    unittest.main()
