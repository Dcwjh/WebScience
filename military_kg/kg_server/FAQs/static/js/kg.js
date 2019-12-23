var myChart = echarts.init(document.getElementById('presentation'));
var option = {
        series: [
            {
                type: 'graph',
                layout: 'force',
                symbolSize: 20,
                roam: true,
                edgeSymbol: ['circle', 'arrow'],
                edgeSymbolSize: [2, 6],
                edgeLabel: {
                    normal: {
                        textStyle: {
                            fontSize: 8
                        }
                    }
                },
                force: {
                    repulsion: 2500,
                    edgeLength: [5, 20]
                },
                draggable: true,
                itemStyle: {
                    normal: {
                        color: '#4b565b'
                    }
                },
                lineStyle: {
                    normal: {
                        width: 1,
                        color: '#4b565b'
                    }
                },
                edgeLabel: {
                    normal: {
                        show: true,
                        formatter: function (x) {
                            return x.data.name;
                        }
                    }
                },
                label: {
                    normal: {
                        show: true,
                        textStyle: {
                        }
                    }
                },
                data: [],
                links: []
            }
        ]
};

$(function(){
    var keyword = getQueryString('keyword');
    if (keyword!=null){
    $("input[name='keyword']").val(keyword);
    $.ajax({
            async: false,
            url: './show',
            type: 'get',
            data: {'keyword':keyword},
            success: function(data){
                var res = data['ans'];
                var nodes = new Set();
                for(var i=0;i<res.length;i++){
                    nodes.add(res[i]['e1']);
                    nodes.add(res[i]['e2']);
                }
                nodes.forEach(function(node){
                    option.series[0].data.push({name:node})
                });

                for(var i=0;i<res.length;i++){
                var link = {
                        source:res[i].e1,
                        target:res[i].e2,
                        name:res[i].r
                    }
                    option.series[0].links.push(link);
                }
                myChart.setOption(option);
            }
        })
    }
});

$("#search-btn").click(function(){
    var $form = $(this).parent();
    var $keyword = $form.find('input[name="keyword"]');
    var content = $.trim($keyword.val());
    if(content.length == 0){
        showAlert("输入内容不能为空")
    }else{
        $.ajax({
            async: false,
            url: './show',
            type: 'get',
            data: {'keyword':content},
            success: function(data){
                var res = data['ans'];
                var nodes = new Set();
                for(var i=0;i<res.length;i++){
                    nodes.add(res[i]['e1']);
                    nodes.add(res[i]['e2']);
                }
                nodes.forEach(function(node){
                    option.series[0].data.push({name:node})
                });

                for(var i=0;i<res.length;i++){
                var link = {
                        source:res[i].e1,
                        target:res[i].e2,
                        name:res[i].r
                    }
                    option.series[0].links.push(link);
                }
                myChart.setOption(option);
            }
        })
    }
});

function showAlert(msg){
    $.alert({
        title: '注意！',
        content: msg,
    });
}

function getQueryString(name) {
	  var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
	  var r = window.location.search.substr(1).match(reg);
	  if (r != null) return decodeURI(r[2]); return null;
}