$("#search-btn").click(function(){

    var $form = $(this).parent();
    var $question = $form.find('input[name="question"]');
    var content = $.trim($question.val());
    if(content.length == 0){
        showAlert("输入内容不能为空")
    }else{
        $('#search-result').mLoading("show");//显示loading组件
        $.ajax({
            async: false,
            url: './search',
            type: 'get',
            data: {'question':content},
            success: function(data){
                $('#search-result').mLoading("hide");//隐藏loading组件
                $("#search-result").html('');
                var res = data['ans'];
                console.log(res)
                for(var i=0;i<res.length;i++){
                    var item = '<div class="panel panel-default"><div class="panel-body"><a href="./kg_search/?keyword='+res[i]+'">'+res[i]+'</a></div></div>';
                    $("#search-result").append(item);
                }
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

