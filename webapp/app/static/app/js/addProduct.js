var followBtns = document.getElementsByClassName('follow-btn')
for(i = 0; i < followBtns.length; i++){
    followBtns[i].addEventListener('click', function(){
        var story_id = this.dataset.id;
        var action = this.dataset.action;
        console.log(story_id);
        console.log('action: ', action);
        console.log('user: ', user)
        if (user === "AnonymousUser") {
            console.log("User not login");
        } else {
            updateUserOrder(productId, action);
        }
    })
}

function updateUserOrder(productId, action){
    console.log("User login ok");
    console.log("id: ", productId);
    console.log("action 2: ", action);
    var url = '/update_item/';
    fetch(url,{
        method: 'POST',
        headers: {
            'Content-Type':'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({'productId': productId, 'action': action})
    }).then((reponse) =>{
       return reponse.json();
       
    }).then((data) =>{
        console.log('data: ', data)
        location.reload();
    })
}
