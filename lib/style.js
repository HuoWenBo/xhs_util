let style = document.createElement('style')
style.innerText = `
input.labelauty + label {
    display: table;
    font-size: 14px;
    padding: 10px;
    background-color: #efefef;
    color: #000;
    cursor: pointer;

    border-radius: 3px 3px 3px 3px;
    -moz-border-radius: 3px 3px 3px 3px;
    -webkit-border-radius: 3px 3px 3px 3px;

    transition: background-color 0.25s;
    -moz-transition: background-color 0.25s;
    -webkit-transition: background-color 0.25s;
    -o-transition: background-color 0.25s;

    -moz-user-select: none;
    -khtml-user-select: none;
    -webkit-user-select: none;
    -o-user-select: none;
}
input.labelauty + label > span.labelauty-unchecked,
input.labelauty + label > span.labelauty-checked{
    display: inline-block;
    line-height: 16px;
    vertical-align: bottom;
}
input.labelauty + label > span.labelauty-unchecked-image,
input.labelauty + label > span.labelauty-checked-image {
    display: inline-block;
    width: 16px;
    height: 16px;
    vertical-align: bottom;
    background-repeat: no-repeat;
    background-position: left center;

    transition: background-image 0.5s linear;
    -moz-transition: background-image 0.5s linear;
    -webkit-transition: background-image 0.5s linear;
    -o-transition: background-image 0.5s linear;
}

input.labelauty + label > span.labelauty-unchecked-image + span.labelauty-unchecked,
input.labelauty + label > span.labelauty-checked-image + span.labelauty-checked {
    margin-left: 7px;
}

input.labelauty:not(:checked):not([disabled]) + label:hover {
    background-color: #eaeaea;
    color: #a7a7a7;
}
input.labelauty:not(:checked) + label > span.labelauty-checked-image {
    display: none;
}

input.labelauty:not(:checked) + label > span.labelauty-checked {
    display: none;
}

input.labelauty:checked + label {
    background-color: #3498db;
    color: #ffffff;
}

input.labelauty:checked:not([disabled]) + label:hover {
    background-color: #72c5fd;
}
input.labelauty:checked + label > span.labelauty-unchecked-image {
    display: none;
}

input.labelauty:checked + label > span.labelauty-unchecked {
    display: none;
}

input.labelauty:checked + label > span.labelauty-checked {
    display: inline-block;
}

input.labelauty.no-label:checked + label > span.labelauty-checked {
    display: block;
}

input.labelauty[disabled] + label {
    opacity: 0.5;
}

input.labelauty + label > span.labelauty-unchecked-image {
    background-image: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQBAMAAADt3eJSAAAAG1BMVEX///+1tbW1tbW1tbW1tbW1tbW1tbW1tbW1tbWBfVZBAAAACHRSTlMABoiJkJHt7nfRUnAAAAAmSURBVHheYyARMIaVCoAZLB0dCmAGW0dHApwBkzKAKA4HKyYFAAD+EwceuqwZiQAAAABJRU5ErkJggg==");
}

input.labelauty + label > span.labelauty-checked-image {
    background-image: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAZlBMVEX///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////+rG8stAAAAIXRSTlMAAgMKpAGhnbmVnpi4CaqInATAiqKfloSQq6aSB5u9mrT+kbbIAAAAZklEQVR4XqXNNw7DQAxEUXKDcs7Onvtf0uTCwEqFKv2KryCGLsZlZQ/ugGzvFEAR3Tfi3FPt2mCTiBNDNACjehLPLNcCYCXj9F9NrOd2E6dije8IPTz9e2bqF8dB+wY+4pj9yv5ZPz3IB4i29NtOAAAAAElFTkSuQmCC");
}
/*下拉框*/
.short-select{
    background:#fafdfe;
    height:35px;
    width:189px;
    line-height:35px;
    border:1px solid #9bc0dd;
    -moz-border-radius:5px;
    -webkit-border-radius:5px;
    border-radius:5px;
    font-size: 1.1rem;
    text-align: center;
    margin-left: 15px;
}
/*复选框*/
ul { list-style-type: none;}
li { display: inline-block;}
li { margin: 5px 3px; text-align: center;}
input.labelauty + label { font: 12px "Microsoft Yahei";}
/*input*/
#user-profession {
    width: 240px;
    border: 1px solid #ccc;
    padding: 7px 0px;
    border-radius: 5px;
    padding-left:5px;
    margin-top: 10px;
    margin-bottom: 30px;
    -webkit-box-shadow: inset 0 1px 1px rgba(0,0,0,.075);
    box-shadow: inset 0 1px 1px rgba(0,0,0,.075);
    -webkit-transition: border-color ease-in-out .15s,-webkit-box-shadow ease-in-out .15s;
    -o-transition: border-color ease-in-out .15s,box-shadow ease-in-out .15s;
    transition: border-color ease-in-out .15s,box-shadow ease-in-out .15s
}
#user-profession:focus {
    border-color: #66afe9;
    outline: 0;
    -webkit-box-shadow: inset 0 1px 1px rgba(0,0,0,.075),0 0 8px rgba(102,175,233,.6);
    box-shadow: inset 0 1px 1px rgba(0,0,0,.075),0 0 8px rgba(102,175,233,.6)
}
/*按钮*/
.btn {
    width: 240px;
    height: 40px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 1.5rem;
    cursor: pointer;
    user-select: none;
    letter-spacing: 1rem;
    text-indent: 1rem;
    border-radius: 10px;
    box-sizing: border-box;
}
.twinkle {
    overflow: hidden;
    position: relative;
    border: 2px solid #2c3e50;
    color: #2c3e50;
    transition: background-color .2s;
}

.twinkle::before {
    content: "";
    position: absolute;
    width: 50px;
    height: 200%;
    background-color: rgba(255, 255, 255, .6);
    transform: skew(45deg) translate3d(-200px,0,0);
}

.twinkle:hover {
    background-color: #2c3e50;
    color: #fff
}

.twinkle:hover::before {
    transition: ease-in-out 0.8s;
    transform: skew(45deg) translate3d(300px,0,0);
}
/*容器*/
#forecast-result-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 280px; /* 调整容器的宽度 */
    background-color: #efefef;
    padding: 20px;
    index-z: 999;
}
#forecast-result-container select, #forecast-result-container select option {
    index-z: 1000;
}
#forecast-result-container, #forecast-result-container * {
    box-sizing: border-box;
}
/* 自定义选中时的样式 */
input[type="checkbox"]:checked + label {
    background-color: #4CAF50;
    color: white;
}
.dowebok {
    padding: 0;
}
    `
document.head.appendChild(style)
