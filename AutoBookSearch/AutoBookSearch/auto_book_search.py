#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
定跡を自動で効率良く探索する
やねうら王v4.87以上推奨
"""

import os
import sys
import subprocess as sp
import configparser

from lib.best_pv_search import BestPVSearch



def main():
    """
    定跡を自動で探索する
    """
    # 作業ディレクトリを自身のファイルのディレクトリに変更
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

    # 設定ファイルのロード
    options = configparser.ConfigParser()
    options.optionxform = str
    options.read('options.ini', encoding='utf-8')


    # 定跡探索
    book_search = BestPVSearch(options)

    # 課題局面までの手順を定跡として作成する
    book_search.make_theme_book()

    # 定跡延長
    for i in range(int(options['Search']['MaxLoops'])):
        print("loop %d/%d" %(i+1, int(options['Search']['MaxLoops'])))
        book_search.search()
        book_search.make_cmd()
        cmd = (options['YaneuraOu']['EngineFile'] + " file "
               + options['Search']['CommandFile'])
        sp.call(cmd.split())


if __name__ == '__main__':
    main()
