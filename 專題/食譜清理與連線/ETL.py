import pandas as pd
import os,json,re,csv,pymongo,sys

#參數
#讀取路徑
path=r"F:\資策會\專題\爬蟲\venv\collction_freefood_11_23"
#輸出路徑
path2=r"F:\資策會\專題\爬蟲\venv\collction_freefood_clean"
#mongo設定
mongo_db="test"
mongo_db_collection="food4"


if not os.path.exists(path2): #沒有這個資料夾就新創資料夾
    os.mkdir(path2)
if not os.path.exists(path):
    os.mkdir(path)

# def trans(str,unicode_down,unicode_up):
#     for i in range(int("0x"+unicode_down,16),int("0x"+unicode_down,16)):
#         if ord(str)==i:
#             #將大寫數字轉成小寫數字，ord()可將字串轉成utf-8十進制整数 chr()則是反函數,觀察全形和半形差65248變可轉換 半形數字0-9
#             return chr(ord(str)-65248)
#         else:
#             pass
#
# trans("１","FF10","uFF19")
def split_ingredient_units_to_number(ingredient_units_clean):
    try:
        x=re.search(r"\d*.?\d",ingredient_units_clean)
        if x:
            number=x.group()
            number=str(float(number))
            return number
    except TypeError as e:
        print(e)

def split_ingredient_units_to_unit(ingredient_units_clean):
    try:
        unit=re.findall(r"[^0-9.]",ingredient_units_clean)
        if unit:
            unit=",".join(unit).replace(",","")
            return unit
    except TypeError as e:
        print(e)
#設定欄位輸出成csv
def csv_to_out(recipe_name,ingredient_names_clean,number,unit):
    with open('free_food_clean_recipename_ingredientnames_number_unit.csv', 'a+', newline='', encoding="utf-8") as csvfile:
        try:
            writer = csv.writer(csvfile)
            try:
                lista=[recipe_name,ingredient_names_clean,number,unit]
                #print(lista)
                #藉由join產生的ERROR來做到，食物與數字與單位同時存在的篩選
                a=",".join(lista).split(",")
                #print(a)
                writer.writerow(a)
            except JSONDecodeError as e:
                print(e)
            except NameError as e:
                print(e)
        except NameError as e:
            print(e)
        except JSONDecodeError as e:
            print(e)

def fraction_to_float(s):
    list_str=list(s.group())
    n=round(int(list_str[0])/int(list_str[2]),3)
    return str(n)+",".join(list_str[3:]).replace(",","")


def clean_food(ingredient_names):
    a = ingredient_names.replace("半", "0.5").replace("１", "1").replace("０", "1").replace("２", "2") \
        .replace("３", "3").replace("４", "4").replace("５", "5").replace("（", "(").replace("）", ")")
    b = re.split(r"\d", a)[0]
    #中文、大寫英文、小寫英文
    c = re.sub(r"([^\u4e00-\u9fa5\u0041-\u005A\u0061-\u007A]|一(包|碗|小碗|附)|(適|少)(量|當|許)|新鮮|市售|\
    |隔夜|切(段|絲|成|塊|片|碎末|花|碎|小丁|丁|末|細|條|小(塊|段))|約|(或|可(不用|用|依|選|均勻|不加|視家裡|\
    |替換|省略|切分|以)).*)|(皆|亦|即|也|均)可|(此次|一(個|支|大匙|小(撮|匙)|隻|把)|(依|視)個人|又(稱|名)).*|\
    |兩(?!節|層).*|數.*|少|個人包|成分|手切|去(皮|骨)|帶皮|現炒|原味|吃剩的|一(?!即|般)|小$.*|斜段|大碗|\
    |份量|沾醬|方便製作的|宜口為主|建議|表面裝飾", "", b)
    d = re.sub(r"各$|各(式|種)|片狀|特級冷壓初榨|剝殼|方便製作的份量|不同|小(丁|束)|酌量|茄子重量的|沒餡|付煮熟|\
    |幾滴|裝飾用|煮切|去殼|醃料分成|鍋子.*", "", c)
    ingredient_names = re.sub("飯{2}", "飯", d)
    return ingredient_names

def clean_unit(ingredient_units):
    # 要有順序性的取代，否則有反效果，一開始就用RE模組可能誤抓
    ingredient_units = re.sub(r"半\b", "", ingredient_units).replace("1小半", "0.5").replace("小半", "0.5") \
        .replace("一半", "0.5").replace("半", "0.5").replace("1½", "1.5").replace("½", "0.5").replace("⅓", "0.333") \
        .replace("數", "x").replace("／","/").replace("～","~")\
        .replace("一般", "").replace("一", "1").replace("１", "1").replace("０", "1").replace("２", "2") \
        .replace("３", "3").replace("４", "4").replace("５", "5").replace("（", "(").replace("）", ")")
    # 找全形數字
    k = re.search(r"[\uFF10-\uFF19]", ingredient_units)
    if k:
        print(k.group())
    else:
        pass
    # 怕這些形容詞在真正的單位詞前面
    list_ingredient_units = ["適量", "酌量", "少量", "幾片", "幾滴", "少許", "些許"]
    for n, j in enumerate(list_ingredient_units):
        ingredient_units = ingredient_units.replace(str(j),"5g")
    try:
        ingredient_units = re.search(r"(([0-9]|x).*)", ingredient_units)
        ingredient_units = ingredient_units.group()
        ingredient_units = re.sub(r"(\({1}\D*\))", "", ingredient_units)
        ingredient_units = re.sub(r"\(百分比.*", "", ingredient_units)
        ingredient_units = re.sub(r"c+\.c+\.?", "cc", ingredient_units)
        ingredient_units = ingredient_units.replace("，依個人喜好調整", "").replace("約", "").replace(",", "")
        ingredient_units = re.sub(r"\s", "", ingredient_units)

        ingredient_units = re.sub(r"的量*", "", ingredient_units)
        #轉換數量從分數變成小數 1/2=>0.5

        ingredient_units = re.sub(r"\d(\／|\/)\d.*", fraction_to_float, ingredient_units)
        return ingredient_units
        x = re.search(r"\d*(k)?(g|公克|克)", ingredient_units)
        if x:
            # 有KG被抓進來
            ingredient_units = x.group()
            return ingredient_units
        else:
            y= re.search(r"(\~|\∼|\-).*", ingredient_units)
            if y:
                ingredient_units = y.group()
                ingredient_units=ingredient_units.replace("~","").replace("∼","")
                return ingredient_units
            else:
                return ingredient_units
    except NameError as e:
        print(e)
    except AttributeError as e:
        print(e)
def write_file_to_mongo(clean_json_list,mongo_db,mongo_db_collection):
    # You're trying to call a method from a string. This is not specific(具體) to pymongo.
    #mongo_db.mongo_db_collection.insert_many(clean_json_list) 不能這樣寫，但不會有ERROR
    mongo_db[mongo_db_collection].insert_many(clean_json_list)

def load_file_from_mongo(mongo_db,mongo_db_collection):
    collections = [str(mongo_db_collection)]
    try:
        read_categories = mongo_db[collections[0]].find()
        for i in read_categories:
            #return i
            print(i)
    except:
        print(sys.exc_info())

def clean(path):
    #讀所有json
    json_list=os.listdir(path)
    list_for_collect_clean_food=[]
    for j in json_list:
        try:
            with open(path + "/" + j, "r", encoding="utf-8") as f:
                try:
                    dic = f.read()
                    d = json.loads(dic)
                    recipe_name = d["recipe_name"]
                    list_ingredients = d["ingredients"]
                    for i in list_ingredients:
                        #清理食材
                        ingredient_names = i["ingredient_names"]
                        ingredient_names_clean=clean_food(ingredient_names)

                        #清理數量與單位
                        ingredient_units=i["ingredient_units"]
                        ingredient_units_clean=clean_unit(ingredient_units)

                        #分隔數量與單位
                        number=split_ingredient_units_to_number(ingredient_units_clean)
                        unit=split_ingredient_units_to_unit(ingredient_units_clean)

                        #輸出成CSV
                        #csv_to_out(recipe_name,ingredient_names_clean,number,unit)

                        #寫回json,輸出
                        i["ingredient_names"]=ingredient_names_clean
                        i["ingredient_quantity"]=number
                        i["ingredient_units"]=unit
                        #顯示在畫面
                        #print(ingredient_units_clean,"        ",number,"        ",unit)
                    #顯示清理後每個json
                    #print(d)
                    list_for_collect_clean_food.append(d)

                except ValueError as e:
                    print(e)
                except JSONDecodeError as e:
                    print(e)
        except PermissionError as e:
            print(e)
        except FileNotFoundError as e:
            print(e)
    #print(list_for_collect_clean_food)
    return list_for_collect_clean_food

#將資料全部存成一個txt檔，在讀取的時候會容易造成memory ERROR，後續不沿用此FUN
def out_put_txt(clean_json_list):
    with open("clean_json_list6.txt","w+",encoding="utf-8") as f:
        for i in clean_json_list:
            f.write(str(i)+"\n")
        f.close()

def output_json(clean_json_list):
    for n,i in enumerate(clean_json_list):
        with open("%s/food_json_%s.json" % (path2, n), "a+", encoding="utf-8") as f:
            json.dump(i, f, ensure_ascii=False)




def main(path,mongo_db,mongo_db_collection):
    clean_json_list = clean(path)
    output_json(clean_json_list)
    #out_put_txt(clean_json_list)
    #write_file_to_mongo(clean_json_list,mongo_db,mongo_db_collection)
    #load_file_from_mongo(mongo_db,mongo_db_collection)

if __name__ == "__main__":
    # 建立連線  品傑36.228.69.179
    client = pymongo.MongoClient('mongodb://%s:%s@%s:%s/' % ('root', 'root', 'localhost', '27017'))
    # 寫法client.mongo_db 的問題 跟def write_file_to_mongo時候一樣
    mongo_db = client[mongo_db]
    main(path,mongo_db,mongo_db_collection)





