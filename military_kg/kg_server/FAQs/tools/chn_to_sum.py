cn_sum = {
      '〇': '0', '一': '1', '二': '2', '三': '3', '四': '4', '五': '5', '六': '6', '七': '7', '八': '8', '九': '9', '零': '0',
      '壹': '1', '贰': '2', '叁': '3', '肆': '4', '伍': '5', '陆': '6', '柒': '7', '捌': '8', '玖': '9', '貮': '2', '两': '2',
}

cn_unit = {
     '十': 10,
     '拾': 10,
     '百': 100,
     '佰': 100,
     '千': 1000,
     '仟': 1000,
     '万': 10000,
     '萬': 10000,
     '亿': 100000000,
     '億': 100000000,
     '兆': 1000000000000,
     '角': 0.1,
     '分': 0.01
}

def chn_to_sum(chn):
     # 传入字符串
     sum = 0
     lis = []
     flo = False
     str_flo = ''
     for i in chn:
         if flo:
             if i in cn_sum:
                 str_flo += cn_sum[i]
             if i in cn_unit:
                 lis.append(cn_unit[i])
         else:
             if i == '点':
                 flo = True
             if i in cn_sum:
                 lis.append(cn_sum[i])
             if i in cn_unit:
                 lis.append(cn_unit[i])
     for k in range(len(lis)):
         if k == len(lis)-1:
             if str_flo:
                 sum += float('.'+str_flo)
             if type(lis[k]) == str:
                 sum = sum+int(lis[k])
         if type(lis[k]) in [int, float]:
             if lis[k] > sum:
                 sum = (sum+int(lis[k-1]))*lis[k]
             else:
                 sum = sum + (int(lis[k-1])*lis[k])

     return round(sum, 2)