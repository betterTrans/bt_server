import dataset


def upsert_id(table, data, key):
    is_new = True
    id = table.upsert(data, key)
    if isinstance(id, bool): # Update 【修改】
        is_new = False
        id = table.find_one(**data)['id']
        
    return id, is_new

def saveTerm(record_to_save):
    return_str = ''
    with dataset.connect(f'sqlite:///db/bt_server.db') as db:
        table = db['terms']

        id, is_new = upsert_id(table, record_to_save, ['ot_text', 'mt_text', 'tt_text'])

    return_str = f"Term#{id}:{record_to_save['ot_text']}："+\
                (record_to_save['mt_text']+"=》" if (record_to_save['mt_text']) else "")+\
                (record_to_save['tt_text'] if (record_to_save['tt_text']) else "")+\
                (" 記錄已新增..." if is_new else " 記錄已更新...")

    return return_str

def deleteTerm(record_to_delete):
    return_str = ''
    with dataset.connect(f'sqlite:///db/bt_server.db') as db:
        table = db['terms']
        deleted = table.delete(
            ot_text=record_to_delete["ot_text"],
            mt_text=record_to_delete["mt_text"],
            tt_text=record_to_delete["tt_text"])

        return_str = f"Term:{record_to_delete['ot_text']}："+\
                    (record_to_delete['mt_text']+"=》" if (record_to_delete['mt_text']) else "")+\
                    (record_to_delete['tt_text'] if (record_to_delete['tt_text']) else "")+\
                    (" 記錄已刪除..." if deleted else " 這筆記錄並不存在...")

    return return_str

# 針對句子中的每個 token，查詢相應的機譯人譯。所需的資料結構如下
#saved_terms = {
#    token#1 : [  // 以 token 為索引
#        {
#          ot_text: aaa,
#          mt_text: bbb, 
#          tt_text: ccc,
#        },
#        {第二種解釋},
#        ...
#    ]
#    ...
#}
def getTerms(tokens):
    saved_terms = {}
    with dataset.connect(f'sqlite:///db/bt_server.db') as db:
        table = db['terms']
        
        for token in tokens:
            records = [r for r in table.find(ot_text=token)]
            if records:
                saved_terms[token]=records    # 掛上查到的所有解釋

    return saved_terms
