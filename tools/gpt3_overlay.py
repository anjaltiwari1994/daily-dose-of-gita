import base64,json
from playwright.sync_api import sync_playwright
import gen
B='/home/claude/daily-dose-of-gita/bgbank/'
I=[
('n04','3','35','Comparing your life to others?','YOUR OWN PATH',"Your own path, imperfect, beats another's.",'श्रेयान्स्वधर्मो विगुणः परधर्मात्स्वनुष्ठितात्।\nस्वधर्मे निधनं श्रेयः परधर्मो भयावहः॥',None),
('n12','3','8','Procrastinating again?','ACTION','Action is better than inaction. Do your work.','नियतं कुरु कर्म त्वं कर्म ज्यायो ह्यकर्मणः।\nशरीरयात्रापि च ते न प्रसिद्ध्येदकर्मणः॥',None),
('n02','3','9',"Want work that doesn't drain you?",'SELFLESS WORK','Work done as an offering sets you free.','यज्ञार्थात्कर्मणोऽन्यत्र लोकोऽयं कर्मबन्धनः।\nतदर्थं कर्म कौन्तेय मुक्तसङ्गः समाचर॥','Turn work into freedom'),
('n03','4','40','Stuck in constant doubt?','DOUBT','Doubt destroys. Faith brings peace.','अज्ञश्चाश्रद्दधानश्च संशयात्मा विनश्यति।\nनायं लोकोऽस्ति न परो न सुखं संशयात्मनः॥',None),
('n05','2','3','Feel like giving up?','COURAGE',"Don't give in to weakness. Rise, Arjuna.",'क्लैब्यं मा स्म गमः पार्थ नैतत्त्वय्युपपद्यते।\nक्षुद्रं हृदयदौर्बल्यं त्यक्त्वोत्तिष्ठ परन्तप॥',None),
('n08','4','38','The purest thing you can chase','KNOWLEDGE','Nothing purifies like knowledge.','न हि ज्ञानेन सदृशं पवित्रमिह विद्यते।\nतत्स्वयं योगसंसिद्धः कालेनात्मनि विन्दति॥',None),
('n06','18','58','Obstacle feels too big?','OBSTACLES','Fix your mind on Me and cross every obstacle.','मच्चित्तः सर्वदुर्गाणि मत्प्रसादात्तरिष्यसि।\nअथ चेत्त्वमहङ्कारान्न श्रोष्यसि विनङ्क्ष्यसि॥',None),
('n22','2','66',"Can't find peace of mind?",'PEACE','Without a steady mind there is no peace.','नास्ति बुद्धिरयुक्तस्य न चायुक्तस्य भावना।\nन चाभावयतः शान्तिरशान्तस्य कुतः सुखम्॥','How to find calm in 3 steps'),
('n23','18','45','Want to master your craft?','YOUR CRAFT','Devotion to your own work leads to perfection.','स्वे स्वे कर्मण्यभिरतः संसिद्धिं लभते नरः।\nस्वकर्मनिरतः सिद्धिं यथा विन्दति तच्छृणु॥','3 steps to master your craft'),
('n07','3','43','Wish you had more self-control?','SELF-CONTROL','Know the Self, steady the mind, conquer desire.','एवं बुद्धेः परं बुद्ध्वा संस्तभ्यात्मानमात्मना।\nजहि शत्रुं महाबाहो कामरूपं दुरासदम्॥','3 ways to build self-control'),
('n09','6','40','Worried your effort is wasted?','EFFORT','No effort is ever lost, here or beyond.','पार्थ नैवेह नामुत्र विनाशस्तस्य विद्यते।\nनहि कल्याणकृत्कश्चिद्दुर्गतिं तात गच्छति॥',None),
('n11','6','26','Mind wandering again?','MINDFULNESS','When the mind wanders, gently bring it back.','यतो यतो निश्चरति मनश्चञ्चलमस्थिरम्।\nततस्ततो नियम्यैतदात्मन्येव वशं नयेत्॥',None),
('n10','2','64','Looking for inner peace?','INNER PEACE','Self-control brings lasting peace.','रागद्वेषवियुक्तैस्तु विषयानिन्द्रियैश्चरन्।\nआत्मवश्यैर्विधेयात्मा प्रसादमधिगच्छति॥',None),
('n14','18','37','Hard now, sweet later?','DISCIPLINE','Bitter at first, nectar in the end.','यत्तदग्रे विषमिव परिणामेऽमृतोपमम्।\nतत्सुखं सात्त्विकं प्रोक्तमात्मबुद्धिप्रसादजम्॥','How to make discipline easier'),
('n20','9','27','Make ordinary work meaningful?','SACRED WORK','Offer everything you do, and it becomes sacred.','यत्करोषि यदश्नासि यज्जुहोषि ददासि यत्।\nयत्तपस्यसि कौन्तेय तत्कुरुष्व मदर्पणम्॥','Turn any task into something sacred'),
]
def page(it,b64):
    h=gen.page(it,'',0,it['pill'],it['hook'],it['mean'])
    return h.replace("#art{position:absolute;left:0;top:235px;width:1080px;height:1064px;background:url(data:image/png;base64,) center/100% 100%}",
      f"#art{{position:absolute;left:0;top:0;width:1080px;height:1350px;background:url(data:image/png;base64,{b64}) center/cover}}")
out='/home/claude/daily-dose-of-gita/cards';ban=[]
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1080,'height':1350})
    for bg,ch,v,hook,pill,mean,san,bn in I:
        it=dict(ch=ch,v=v,san=san,hook=hook,pill=pill,mean=mean)
        b64=base64.b64encode(open(B+bg+'.png','rb').read()).decode()
        h=page(it,b64);assert 'cover' in h
        pg.set_content(h);pg.wait_for_timeout(600);print(ch,v,pg.evaluate(gen.FIT))
        fn=f'gpt_{ch}_{v}';pg.screenshot(path=f'{out}/{fn}.png')
        if bn: ban.append({'src':f'{out}/{fn}.png','file':fn+'_hook','hook':bn,'handle':'@daily.doseofgita'})
    b.close()
json.dump(ban,open('gpt3_banners.json','w'))
