function __crop__(image_src, get_input) {
    document.getElementById('src_img').hidden = 'True'
    document.getElementById('dst_img').hidden = 'True'
    document.getElementById('loading').hidden = ''
    document.getElementById('choose').disabled = 'disabled'
    document.getElementById('url').disabled = 'disabled'
    document.getElementById('choose_url').disabled = 'disabled'
    document.getElementById("dst_canvas").hidden = 'True'

    var image = new Image();
    var c = document.getElementById("src_canvas")
    c.hidden = ''
    var ctx = c.getContext("2d");
    image.onload = function() {
        ratio = 1.0
        if(image.width > 1024){
            ratio = 1024.0/image.width
        }
        width = ratio*image.width
        height = ratio*image.height
        ctx.canvas.width  = width;
        ctx.canvas.height = height;

        ctx.drawImage(image, 0, 0, width, height);
    };
    image.src = image_src

    Algorithmia.client("simYwF1W5IInfoMltCgjwEPem5G1")
       .algo("algo://wuhuikai/A2RL_online/0.3.2")
       .pipe(get_input())
       .then(function(output) {
            console.log(output)
            document.getElementById('loading').hidden = 'True'
            document.getElementById('choose').disabled = ''
            document.getElementById('url').disabled = ''
                document.getElementById('choose_url').disabled = ''
            var xmin = output.result[0][0]; var ymin = output.result[0][1];
            var xmax = output.result[0][2]; var ymax = output.result[0][3];
            var width = xmax - xmin; var height = ymax - ymin;

            image = new Image();
            var c = document.getElementById("dst_canvas")
            c.hidden = ''
            var ctx = c.getContext("2d");
            image.onload = function() {
                xmin = xmin*image.width;ymin = ymin*image.height;
                width = width*image.width;height = height*image.height;

                ctx.canvas.width  = width;
                ctx.canvas.height = height;
                ctx.drawImage(image, xmin, ymin, width, height, 0, 0, width, height);
            };
            image.src = image_src
       });
}

function crop(){
    document.getElementById('file-input').click();
    document.getElementById('file-input').onchange = function (evt) {
        var tgt = evt.target || window.event.srcElement;
        files = tgt.files;

        // FileReader support
        if (FileReader && files && files.length) {
            var reader = new FileReader();
            reader.onload = function () {
                __crop__(reader.result,
                         function () {
                            return {'type':  'B',
                                    'image': document.getElementById('src_canvas').toDataURL('image/jpeg', 1.0)};
                         })
            }
            reader.readAsDataURL(files[0]);
        }
        // Not supported
        else {
            alert("Change another browser!!!")
        }
    }
}

function crop_url(){
    url = document.getElementById('url').value;

    __crop__(url, function () {
                    return {'type': 'U', 'url': url};
                  })
}
