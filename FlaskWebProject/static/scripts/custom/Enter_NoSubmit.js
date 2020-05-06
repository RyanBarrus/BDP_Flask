document.addEventListener('keydown', function (event) {
            if (event.keyCode === 13) {
                var form = event.target.form;
                var index = Array.prototype.indexOf.call(form, event.target);
                form.elements[index + 1].focus();
                event.preventDefault();
            }
        });
