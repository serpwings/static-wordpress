# -*- coding: utf-8 -*-

"""
STATIC WORDPRESS: WordPress as Static Site Generator
A Python Package for Converting WordPress Installation to a Static Website
https://github.com/serpwings/staticwordpress

    src\staticwordpress\gui\table.py
    
    Copyright (C) 2020-2024 Faisal Shahzad <info@serpwings.com>

<LICENSE_BLOCK>
The contents of this file are subject to version 3 of the 
GNU General Public License (GPL-3.0). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://www.gnu.org/licenses/gpl-3.0.txt
https://github.com/serpwings/staticwordpress/blob/master/LICENSE


Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>
"""


# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# 3rd PARTY LIBRARY IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from PyQt5.QtCore import (
    Qt,
    QAbstractTableModel,
    QModelIndex,
    QVariant,
    QSortFilterProxyModel,
)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPLEMENATIONS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++


class SWDataTable(QAbstractTableModel):
    def __init__(self, data_: list = [], header_: list = []):
        super(SWDataTable, self).__init__()
        self._data = data_
        self._header = header_

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._header[section])

        return QVariant()

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data[index.row()][index.column()]
            return str(value)

    def rowCount(self, index=QModelIndex()):
        return len(self._data)

    def columnCount(self, index=QModelIndex()):
        return len(self._header)

    def insertRow(self, data, row=0, index=QModelIndex()):
        self.beginInsertRows(QModelIndex(), row, row)
        self._data.insert(0, data)
        self.endInsertRows()
        return True

    def clear(self):
        self.beginResetModel()
        self._data = []
        self.endResetModel()


class DataframeQSortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self):
        super(DataframeQSortFilterProxyModel, self).__init__()
        self.role = SWDataTable.ValueRole

    def lessThan(self, left, right):
        role = self.role
        leftData = self.sourceModel().data(left, role)
        rightData = self.sourceModel().data(right, role)
        if leftData is None:
            return True
        elif rightData is None:
            return False
        elif type(leftData) != type(rightData):
            # don't want to sort at all in these cases, False is just a copout ...
            # should warn user
            return False
        return leftData < rightData
