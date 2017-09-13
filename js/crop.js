function crop(){
    document.getElementById('file-input').click();
    document.getElementById('file-input').onchange = function (evt) {
        var tgt = evt.target || window.event.srcElement,
            files = tgt.files;

        // FileReader support
        if (FileReader && files && files.length) {
            var reader = new FileReader();
            reader.onload = function () {
                document.getElementById('src_img').hidden = 'True'
                document.getElementById('dst_img').hidden = 'True'
                document.getElementById('loading').hidden = ''
                document.getElementById('choose').disabled = 'disabled'
                document.getElementById("dst_canvas").hidden = 'True'

                var image = new Image();
                var c = document.getElementById("src_canvas")
                c.hidden = ''
                var ctx = c.getContext("2d");
                image.onload = function() {
                    ctx.canvas.width  = image.width;
                    ctx.canvas.height = image.height;
                    ctx.drawImage(image, 0, 0, image.width, image.height);
                };
                image.src = reader.result

                Algorithmia.client("sim/vFIfNOvubLyPVoNa7L21roe1")
                           .algo("algo://wuhuikai/A2RL")
                           .pipe({'image': reader.result})
                           .then(function(output) {
                                document.getElementById('loading').hidden = 'True'
                                document.getElementById('choose').disabled = ''

                                var xmin = output.result[0][0]; var ymin = output.result[0][1];
                                var xmax = output.result[0][2]; var ymax = output.result[0][3];
                                var width = xmax - xmin; var height = ymax - ymin;

                                var image = new Image();
                                var c = document.getElementById("dst_canvas")
                                c.hidden = ''
                                var ctx = c.getContext("2d");
                                image.onload = function() {
                                    ctx.canvas.width  = width;
                                    ctx.canvas.height = height;
                                    ctx.drawImage(image, xmin, ymin, width, height, 0, 0, width, height);
                                };
                                image.src = reader.result
                           });
            }
            reader.readAsDataURL(files[0]);
        }
        // Not supported
        else {
            alert("Change another browser!!!")
        }
    }
}