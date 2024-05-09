jQuery(function($)
{
    // 탑메뉴 드롭다운
    $('#topmenu').ready(function()
    {
        var self = $(this),
            md1 = self.find('.md1'),
            ml = md1.find('.ml'),
            mla = ml.find('.mla'),
            md2 = ml.find('.md2'),
            cl = md2.find('.cl'),
            cla = cl.find('.cla');

            ml.each(function(idx)
            {
              var self = $(this),
                  a_mla = self.find('.mla'),
                  ul_md2 = self.find('.md2');

              a_mla.bind('focus, mouseenter',function(){
                mla.removeClass('active');
                a_mla.addClass('active');
                md2.hide();
                ul_md2.show();
              });
              ul_md2.bind('blur mouseleave', function(){
                mla.removeClass('active');
                md2.hide();
              });
            });
    });

    //쿠키 생성
    function setCookie(name, value, expiredays){
    	var today = new Date();
	    today.setDate(today.getDate() + expiredays);
	    document.cookie = name + '=' + escape(value) + '; path=/; expires=' + today.toGMTString() + ';'
    }

    //쿠키 확인
    function getCookie(name) {
        var cName = name + "=";
        var x = 0;
        var i = 0

        while ( i <= document.cookie.length ) {
            var y = (x+cName.length);

            if ( document.cookie.substring( x, y ) == cName ) {

                if ( (endOfCookie=document.cookie.indexOf( ";", y )) == -1 )
                    endOfCookie = document.cookie.length;

                return unescape( document.cookie.substring( y, endOfCookie ) );
            }

            x = document.cookie.indexOf( " ", x ) + 1;

            if ( x == 0 )
                break;
        }
        return "";
    }

    //팝업 닫기 버튼 클릭시 동작
    $('.popupclosebutton').click(function (e) {
        var $this = $(this);
        var prt = $this.parent().parent();
        var id = prt.attr('id');

        if (($('#'+id+'check').prop("checked")))
            setCookie(id, 'Y', 1);
        prt.hide('fade');
    });

    //페이지 로드시 반복문으로 쿠키 확인
    $(window).ready(function(){
        for(var i = 0; i < $('#popup').children().length; i++){
            var id = $('#popup').children()[i].id;
            console.log(getCookie(id));
            if(getCookie(id)=="Y"){
                $("#"+id).hide();
            }
        }
    });


    // 메인 베너
$('.banner-box').each(function(index)
{
  var show_count = 5,
    isStop = false,
    timer = 2000,
    slide_time = 1000,
    timer_index = 0,
    self = $(this),
    list = self.find('.list'),
    box = self.find('.box'),
    ol = self.find('ol'),
    li = ol.find('li'),
    li_length = li.length,
    dumy_li = li.clone();

  if(li_length <= show_count) return;

  ol.append(dumy_li);
  li = ol.find('li');

  var prev = $('<a class="prev"><span>[PREV]</span></a>'),
    next = $('<a class="next"><span>[NEXT]</span></a>');

  list.append(prev).append(next);

  function li_width(idx)
  {
    var width = 0;

    for(var i=0; i<=idx; i++)
    {
      width += li.eq(i).outerWidth();
    }

    return width;
  }

  self.find('ol, ol a, a.prev, a.next').bind('focus mouseenter', function(e)
  {
    isStop = true;
    ol.addClass('active');
  })
  .bind('blur mouseleave', function(e)
  {
    isStop = false;
    ol.removeClass('active');
  });

  function board_timer()
  {
    if(isStop)
    {
      return;
    }

    if(timer_index >= li_length)
    {
      timer_index = 0;
      ol.css('margin-left', 0);
    }

    ol.stop().animate({ 'margin-left' : -1 * li_width(timer_index) }, slide_time);
    timer_index++;
  }

  prev.click(function(e)
  {
    e.preventDefault();
    timer_index--;
    if(timer_index < 0)
    {
      timer_index = li_length;
      ol.stop().css({ 'margin-left' : -1 * li_width(timer_index) });
      timer_index--;
    }
    ol.attr('title', timer_index).stop().animate({ 'margin-left' : -1 * li_width(timer_index) }, slide_time);
  });

  next.click(function(e)
  {
    e.preventDefault();
    timer_index++;
    if(timer_index >= li_length)
    {
      timer_index = 0;
      ol.stop().css('margin-left', 0);
    }
    ol.stop().animate({ 'margin-left' : -1 * li_width(timer_index) }, slide_time);
  });

  setInterval(board_timer, timer);
});


    // 메인이미지 처리
    $('.main_image').each(function(index)
	{
		var box = $(this),
			listbox = box.find('> ol, > ul'),
			list = listbox.find('> li'),
			length = list.length,
			max_print_no = 0,
			show_slide_count_min = 1,			// 화면에 보이는 최소 슬라이드
			show_slide_count = 1,				// 한번에 보일 슬라이드 수
			show_slide_css = {
				'position' : 'absolute',
				'left' : 0,
				'top' : 0,
				'z-index' : 1
			},									// 슬라이드 position 타입
			used_fade_effect = true,			// 페이드 효과 사용 여부
			mouse_over_stop = false,			// 요소에 마우스 오버시 멈춤 처리
			play_stop_one_button = true,		// 시작 종료 버튼 하나로 처리
			prev_button = true,					// 이전 버튼 사용 여부
			next_button = true,					// 다음 버튼 사용 여부
			navigation_is_stop = false,			// 시작, 종료 상태 값
			navigation_movie_time = 2000,		// 변경시간
			button_hide = false,				// 버튼 숨기기
			show_list = false;					// 내부 목록보기


		//메인 일경우 설정값 변경
		if(box.hasClass('main_image'))
		{
			navigation_movie_time = 3500;
			show_slide_count_min = 1;
			show_slide_count = 1;
			used_fade_effect = true;
			mouse_over_stop = true;
			show_list = false;
		}

    //배너 일경우 설정값 변경
    if(box.hasClass('banner-box'))
		{
      navigation_movie_time = 1500;
			show_slide_count_min = 5;
			show_slide_count = 5;
			show_slide_css = { 'float' : 'left' };
			mouse_over_stop = true;
			//play_stop_one_button = true;
			//navigation_status = false;
		}




		// 화면에 보이는 슬라이드 수 보다 적을 경우 슬라이드 처리 취소
		if(show_slide_count_min >= length)
		{
			return;
		}

		if(show_slide_count > 0)
		{
			for(var i=0; i<show_slide_count; i++)
			{
				list.parent().append(list.eq(i).clone(true).addClass('clone'));
			}
			list = listbox.find('> li');
		}

		listbox.css('position', 'relative');
		if(show_slide_css) list.css(show_slide_css);

		var pre_idx = 1;
		function navigation_move(idx)
		{
			idx = idx < 0 ? length - 1 : idx;
			idx = idx % length == 0 ? length : idx % length;

			box.find('.navigation_no_list li a').removeClass('active');
			box.find('.navigation_no_list li:nth-child('+ idx +') a').removeClass('active');

			box.find('.navigation_status .now_idx').text(idx);

			if(used_fade_effect)
			{
				list.css('z-index', 1);

				for(var i=pre_idx; i<pre_idx + show_slide_count; i++)
				{
					list.eq(i - 1).css('z-index', 2).show();
				}
				for(var i=idx; i<idx + show_slide_count; i++)
				{
					list.eq(i - 1).css('z-index', 3).hide().fadeIn('slow');
				}
			}
			else
			{
				list.hide();
				for(var i=idx; i<idx + show_slide_count; i++)
				{
					list.eq(i - 1).show();
				}
			}

			pre_idx = idx;
		}

		function navigation_play_stop(isStop)
		{
			navigation_is_stop = typeof(isStop) == 'boolean' ? isStop : !navigation_is_stop;

			if(navigation_is_stop)
			{
				box.find('.navigation_play_stop a.button_play_stop').removeClass('play disable').addClass('stop active').find('span').text('stop');
				box.find('.navigation_play_stop a.button_play').removeClass('active');
				box.find('.navigation_play_stop a.button_stop').addClass('active');
				box.find('.navigation_play_stop a.button_play').addClass('disable');
				box.find('.navigation_play_stop a.button_stop').removeClass('disable');
			}
			else
			{
				box.find('.navigation_play_stop a.button_play_stop').removeClass('stop disable').addClass('play active').find('span').text('play');
				box.find('.navigation_play_stop a.button_play').addClass('active');
				box.find('.navigation_play_stop a.button_stop').removeClass('active');
				box.find('.navigation_play_stop a.button_play').removeClass('disable');
				box.find('.navigation_play_stop a.button_stop').addClass('disable');
			}
		}

		var is_first = true,
			navigation_timer_index = pre_idx;
		function navigation_timer()
		{
			if(navigation_is_stop) return;

			navigation_play_stop(false);

			if(is_first)
			{
				is_first = false;
				navigation_move(navigation_timer_index);
				//navigation_timer_index++;
			}
			else
			{
				navigation_move(navigation_timer_index);
				navigation_timer_index++;
			}
			if(navigation_timer_index > length)
				navigation_timer_index = 1;
		}

		if(length <= max_print_no)
		{
			var no_list = $('<ul class="navigation_no_list"></ul>');
			box.append(no_list);

			for(var i=1;i<=length; i++)
			{
				no_list.append('<li><a class="no-'+ i +'">'+ i +'</a></li>');
			}

			no_list.find('a').each(function(index)
			{
				navigation_move(index + 1);
			});
		}
		else
		{
			var status = $('<div class="navigation_status"></div>');
			status.append('<span class="now_idx">'+ pre_idx +'</span><span class="split">/</span><span class="max_idx">'+ length +'</span>');
			box.append(status);
		}

		var play_stop = $('<div class="navigation_play_stop"></div>');
		box.append(play_stop);

		if(prev_button)
		{
			var button = $('<a class="button_prev prev"><i class="fas fa-angle-left fa-2x"></i></a>');
			play_stop.append(button);
			button.click(function(e)
			{
				e.preventDefault();
				is_first = true;
				navigation_timer_index -= 1;
				navigation_move(navigation_timer_index);
			});
		}

		if(play_stop_one_button)
		{
			var button = $('<a class="button_play_stop"><span>play</span></a>');
			play_stop.append(button);
			button.click(function(e)
			{
				e.preventDefault();
				navigation_play_stop();
			});
		}
		else
		{
			var button_play = $('<a class="button_play play"><span>play</span></a>'),
				button_stop = $('<a class="button_stop stop"><span>stop</span></a>');
			play_stop.append(button_play);
			play_stop.append(button_stop);
			button_play.click(function(e)
			{
				e.preventDefault();
				navigation_play_stop(false);
			});
			button_stop.click(function(e)
			{
				e.preventDefault();
				navigation_play_stop(true);
			});
		}

		if(next_button)
		{
			var button = $('<a class="button_next next"><i class="fas fa-angle-right fa-2x"></i></a>');
			play_stop.append(button);
			button.click(function(e)
			{
				e.preventDefault();
				is_first = true;
				navigation_timer_index += 1;
				navigation_move(navigation_timer_index);
			});
		}

		if(mouse_over_stop)
		{
			list.mouseenter(function(e){ navigation_is_stop = true; }).mouseleave(function(e){ navigation_is_stop = false; });
		}

		if(show_list)
		{
			var showlist = $('<div class="navigation_showlist"><a class="">목록보기</a></div>');
			box.append(showlist);

			showlist.find('a').click(function(e)
			{
				var link = $(this),
					listbox = showlist.find('div.navigation_showlist_listbox');
				if(listbox.length == 0)
				{
					listbox = $('<div class="navigation_showlist_listbox"><ol></ol><div class="txtright"><a class="close">목록닫기</a></div>');

					//list.find('a').each(function(index)
					list.each(function(index)
					{
						var t = $(this),
							clone = t.hasClass('clone'),
							a = t.find('a'),
							href = a.attr('href'),
							target = a.attr('target'),
							text = t.find('img').attr('alt');

						if(!clone)
						{
							if(a.length > 0)
								listbox.find('ol').append('<li><a href="'+ href +'"'+ (target ? ' target="'+ target +'"' : '') +'>'+ text +'</a></li>');
							else
								listbox.find('ol').append('<li>'+ text +'</li>');
						}
					});

					showlist.append(listbox);
					link.text('목록닫기');
					showlist.find('a.close').click(function(e)
					{
						link.text('목록보기');
						listbox.hide();
					});
				}
				else
				{
					if(listbox.is(':visible'))
					{
						listbox.hide();
						link.text('목록보기');
					}
					else
					{
						listbox.show();
						link.text('목록닫기');
					}
				}
			});
		}

		// 네비게이션 타이머 처리
		setInterval(navigation_timer, navigation_movie_time);
	});

	/* 게시판제목 label 처리 */
    $(".subject-box").click(function(){
        $(".subject-box label span").css('display','none');
    });

    $('#topmenu_mb .menu-box .menu-btn a.active').bind('click', function(){
        var self = $(this);
        $('#topmenu_mb .menu-box .md1').animate({left:'0px'});
        $('#topmenu_mb .menu-box .menu-btn a.active').css('z-index', '0');
        $('#topmenu_mb .menu-box .menu-btn a.closes').css('z-index', '9999');
    });
    $('#topmenu_mb .menu-box .menu-btn a.closes').bind('click', function(){
        var self = $(this);
        $('#topmenu_mb .menu-box .md1').animate({left:'-1000px'});
        $('#topmenu_mb .menu-box .menu-btn a.active').css('z-index', '9999');
        $('#topmenu_mb .menu-box .menu-btn a.closes').css('z-index', '0');
    });


    /*
    $('#topmenu_mb .menu-box .menu-btn a.close').click(function(){
        alert('123');
        var self = $(this);
        $('#topmenu_mb .menu-box .md1').animate({left:'-320px'});
        self.addClass('active');
        self.removeClass('close');
    });*/
});
