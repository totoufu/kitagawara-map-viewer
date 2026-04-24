"""
generate_geo_data.py
北川原温 建築プロジェクト65件の緯度経度推定データを生成して projects.json を出力する。
緯度経度は既知情報・所在地名から推定。要手動確認。
"""
import json
import os

# 65件のプロジェクトデータ（緯度経度は所在地から推定）
# lat/lng が None のものは未確定
PROJECTS = [
    {"id": "proj_001", "name": "NADJAの家", "year": 1979, "location": "東京都渋谷区", "lat": 35.6580, "lng": 139.7016, "notes": "推定"},
    {"id": "proj_002", "name": "KCB", "year": 1980, "location": "東京都", "lat": 35.6762, "lng": 139.6503, "notes": "推定"},
    {"id": "proj_003", "name": "S邸", "year": 1980, "location": "東京都", "lat": 35.6895, "lng": 139.7000, "notes": "推定"},
    {"id": "proj_004", "name": "初雁工務店社屋", "year": 1982, "location": "埼玉県川越市", "lat": 35.9247, "lng": 139.4858, "notes": "推定"},
    {"id": "proj_005", "name": "美安温閣", "year": 1984, "location": "東京都", "lat": 35.6762, "lng": 139.7000, "notes": "推定"},
    {"id": "proj_006", "name": "信濃デッサン館槐多庵", "year": 1985, "location": "長野県上田市", "lat": 36.4018, "lng": 138.2514, "notes": "推定"},
    {"id": "proj_007", "name": "RISE", "year": 1986, "location": "東京都渋谷区", "lat": 35.6580, "lng": 139.7016, "notes": "推定"},
    {"id": "proj_008", "name": "395", "year": 1986, "location": "東京都", "lat": 35.6900, "lng": 139.7100, "notes": "推定"},
    {"id": "proj_009", "name": "高輪館", "year": 1986, "location": "東京都港区高輪", "lat": 35.6324, "lng": 139.7290, "notes": "推定"},
    {"id": "proj_010", "name": "小野建設本社屋", "year": 1986, "location": "東京都", "lat": 35.6800, "lng": 139.7600, "notes": "推定"},
    {"id": "proj_011", "name": "KAMERA", "year": 1987, "location": "東京都", "lat": 35.7000, "lng": 139.7100, "notes": "推定"},
    {"id": "proj_012", "name": "メサ", "year": 1988, "location": "東京都", "lat": 35.6950, "lng": 139.7200, "notes": "推定"},
    {"id": "proj_013", "name": "クラウディ スプーン", "year": 1988, "location": "東京都", "lat": 35.6720, "lng": 139.7050, "notes": "推定"},
    {"id": "proj_014", "name": "OK-studio", "year": 1988, "location": "東京都", "lat": 35.7100, "lng": 139.7300, "notes": "推定"},
    {"id": "proj_015", "name": "METROÇA", "year": 1989, "location": "東京都", "lat": 35.6850, "lng": 139.7650, "notes": "推定"},
    {"id": "proj_016", "name": "VASARA", "year": 1989, "location": "東京都", "lat": 35.6700, "lng": 139.7550, "notes": "推定"},
    {"id": "proj_017", "name": "メトロツアー／エドケン東京本社屋", "year": 1989, "location": "東京都", "lat": 35.6780, "lng": 139.7680, "notes": "推定"},
    {"id": "proj_018", "name": "GALA", "year": 1989, "location": "東京都", "lat": 35.6920, "lng": 139.7020, "notes": "推定"},
    {"id": "proj_019", "name": "FAUST", "year": 1989, "location": "東京都", "lat": 35.6760, "lng": 139.7440, "notes": "推定"},
    {"id": "proj_020", "name": "THE INTERNATIONAL", "year": 1989, "location": "東京都港区", "lat": 35.6580, "lng": 139.7454, "notes": "推定"},
    {"id": "proj_021", "name": "サンテロコ／旭ガラスミラーショールーム", "year": 1990, "location": "東京都千代田区", "lat": 35.6938, "lng": 139.7534, "notes": "推定"},
    {"id": "proj_022", "name": "SAPPHO（サッフォー）", "year": 1990, "location": "東京都", "lat": 35.6580, "lng": 139.7016, "notes": "推定"},
    {"id": "proj_023", "name": "織田邸", "year": 1990, "location": "東京都", "lat": 35.7200, "lng": 139.7300, "notes": "推定"},
    {"id": "proj_024", "name": "ギャラリー間〈北川原温の建築〉展", "year": 1990, "location": "東京都港区南青山", "lat": 35.6654, "lng": 139.7196, "notes": "ギャラリー間（南青山）"},
    {"id": "proj_025", "name": "F1／船木商会社屋", "year": 1991, "location": "東京都", "lat": 35.6900, "lng": 139.7700, "notes": "推定"},
    {"id": "proj_026", "name": "サント産業本社屋", "year": 1991, "location": "東京都", "lat": 35.7050, "lng": 139.7400, "notes": "推定"},
    {"id": "proj_027", "name": "茶美会（その4）「素」", "year": 1992, "location": "東京都", "lat": 35.6800, "lng": 139.7600, "notes": "推定"},
    {"id": "proj_028", "name": "東日本橋派出所", "year": 1993, "location": "東京都中央区東日本橋", "lat": 35.6900, "lng": 139.7870, "notes": "東日本橋"},
    {"id": "proj_029", "name": "インビンシブル2", "year": 1993, "location": "東京都", "lat": 35.6760, "lng": 139.7580, "notes": "推定"},
    {"id": "proj_030", "name": "いわきニュータウンセンタービル", "year": 1994, "location": "福島県いわき市", "lat": 37.0500, "lng": 140.8879, "notes": "いわき市"},
    {"id": "proj_031", "name": "池上工業所社宅", "year": 1994, "location": "東京都大田区池上", "lat": 35.5632, "lng": 139.7006, "notes": "池上"},
    {"id": "proj_032", "name": "I邸", "year": 1994, "location": "東京都", "lat": 35.7150, "lng": 139.7250, "notes": "推定"},
    {"id": "proj_033", "name": "ARIA アリア", "year": 1995, "location": "東京都", "lat": 35.6730, "lng": 139.7130, "notes": "推定"},
    {"id": "proj_034", "name": "飯田高校正門", "year": 1997, "location": "長野県飯田市", "lat": 35.5155, "lng": 137.8218, "notes": "飯田市"},
    {"id": "proj_035", "name": "宣伝会議本社屋ビル", "year": 1997, "location": "東京都南青山", "lat": 35.6680, "lng": 139.7220, "notes": "南青山"},
    {"id": "proj_036", "name": "上田市農林漁業体験実習館", "year": 1997, "location": "長野県上田市", "lat": 36.4018, "lng": 138.2514, "notes": "上田市"},
    {"id": "proj_037", "name": "ヴィラ・エステリオ＋サンタリア聖教会", "year": 1997, "location": "長野県", "lat": 36.2048, "lng": 137.9702, "notes": "推定・長野県"},
    {"id": "proj_038", "name": "C邸", "year": 1997, "location": "東京都", "lat": 35.7300, "lng": 139.7050, "notes": "推定"},
    {"id": "proj_039", "name": "長崎港（元船地区）上屋（B棟）", "year": 1998, "location": "長崎県長崎市", "lat": 32.7448, "lng": 129.8736, "notes": "長崎港"},
    {"id": "proj_040", "name": "福島県産業交流館 ビッグパレットふくしま", "year": 1998, "location": "福島県郡山市", "lat": 37.3915, "lng": 140.3830, "notes": "郡山市"},
    {"id": "proj_041", "name": "港区立大平台みなと荘", "year": 1999, "location": "東京都港区", "lat": 35.6580, "lng": 139.7454, "notes": "港区"},
    {"id": "proj_042", "name": "くまもとアートポリス・不知火文化プラザ", "year": 1999, "location": "熊本県宇城市不知火町", "lat": 32.6547, "lng": 130.6540, "notes": "不知火町"},
    {"id": "proj_043", "name": "岐阜県立森林文化アカデミー", "year": 2001, "location": "岐阜県美濃市", "lat": 35.5415, "lng": 136.9100, "notes": "美濃市"},
    {"id": "proj_044", "name": "ヴィラH", "year": 2001, "location": "東京都", "lat": 35.7050, "lng": 139.7600, "notes": "推定"},
    {"id": "proj_045", "name": "日本ペンクラブ", "year": 2002, "location": "東京都文京区", "lat": 35.7081, "lng": 139.7525, "notes": "文京区"},
    {"id": "proj_046", "name": "学校法人 豊昭学園高校", "year": 2003, "location": "東京都豊島区", "lat": 35.7295, "lng": 139.7108, "notes": "豊島区"},
    {"id": "proj_047", "name": "豊島学院高校・昭和鉄道高校 新4号館", "year": 2003, "location": "東京都豊島区", "lat": 35.7298, "lng": 139.7112, "notes": "豊島区"},
    {"id": "proj_048", "name": "豊島学院高校・昭和鉄道高校 新2号館", "year": 2004, "location": "東京都豊島区", "lat": 35.7300, "lng": 139.7115, "notes": "豊島区"},
    {"id": "proj_049", "name": "豊昭学園1号館 東京交通短期大学", "year": 2018, "location": "東京都豊島区", "lat": 35.7302, "lng": 139.7118, "notes": "豊島区"},
    {"id": "proj_050", "name": "豊昭学園6号館 ラーニングセンター", "year": 2022, "location": "東京都豊島区", "lat": 35.7305, "lng": 139.7120, "notes": "豊島区"},
    {"id": "proj_051", "name": "岐阜県立飛騨牛記念館", "year": 2003, "location": "岐阜県高山市", "lat": 36.1461, "lng": 137.2520, "notes": "高山市"},
    {"id": "proj_052", "name": "佐世保新みなとターミナル", "year": 2003, "location": "長崎県佐世保市", "lat": 33.1787, "lng": 129.7154, "notes": "佐世保市"},
    {"id": "proj_053", "name": "シーボン.本社", "year": 2005, "location": "東京都港区", "lat": 35.6656, "lng": 139.7310, "notes": "推定・港区"},
    {"id": "proj_054", "name": "海上の森・望楼", "year": 2005, "location": "愛知県瀬戸市", "lat": 35.2333, "lng": 137.1333, "notes": "海上の森（瀬戸市）"},
    {"id": "proj_055", "name": "木の国サイト情報館", "year": 2006, "location": "岐阜県", "lat": 35.6000, "lng": 136.8000, "notes": "推定・岐阜県"},
    {"id": "proj_056", "name": "PIET", "year": 2007, "location": "東京都", "lat": 35.6900, "lng": 139.7550, "notes": "推定"},
    {"id": "proj_057", "name": "KEYFOREST871228 キース・ヘリング美術館", "year": 2007, "location": "山梨県北杜市小淵沢", "lat": 35.8705, "lng": 138.3080, "notes": "小淵沢"},
    {"id": "proj_058", "name": "ネザーランドダンスシアターⅠ 舞台美術", "year": 2008, "location": "オランダ・ハーグ（国内公演）", "lat": 35.6762, "lng": 139.6503, "notes": "舞台美術・日本公演推定"},
    {"id": "proj_059", "name": "長野県稲荷山養護学校", "year": 2009, "location": "長野県千曲市稲荷山", "lat": 36.5367, "lng": 138.0830, "notes": "千曲市稲荷山"},
    {"id": "proj_060", "name": "ARS", "year": 2009, "location": "東京都", "lat": 35.6810, "lng": 139.7650, "notes": "推定"},
    {"id": "proj_061", "name": "2015年ミラノ国際博覧会 日本館", "year": 2015, "location": "イタリア・ミラノ（国内設計）", "lat": 35.6762, "lng": 139.6503, "notes": "設計地・東京推定"},
    {"id": "proj_062", "name": "小淵沢アートヴィレッジ", "year": 2015, "location": "山梨県北杜市小淵沢", "lat": 35.8715, "lng": 138.3095, "notes": "小淵沢"},
    {"id": "proj_063", "name": "小淵沢駅舎・駅前広場", "year": 2017, "location": "山梨県北杜市小淵沢", "lat": 35.8722, "lng": 138.3068, "notes": "小淵沢駅"},
    {"id": "proj_064", "name": "ナカニシ新本社R&Dセンター RD1", "year": 2018, "location": "滋賀県草津市", "lat": 35.0139, "lng": 135.9606, "notes": "草津市"},
    {"id": "proj_065", "name": "北野建設長野本社", "year": 2021, "location": "長野県長野市", "lat": 36.6513, "lng": 138.1810, "notes": "長野市"},
]

def main():
    out_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "projects.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(PROJECTS, f, ensure_ascii=False, indent=2)
    print(f"OK: {len(PROJECTS)} projects written to {out_path}")

if __name__ == "__main__":
    main()
