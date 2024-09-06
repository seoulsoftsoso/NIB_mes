import datetime
import os

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models import Model
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone


def sign_upload_path(instance, filename):
    return os.path.join('sign', filename)


def logo_upload_path(instance, filename):
    return os.path.join('logo', filename)


def business_certificate_upload_path(instance, filename):
    return os.path.join('certificate', filename)


def item_master_img_upload_path(instance, filename):  # 품목기준정보 이미지 경로
    return os.path.join('item_master_img', filename)


def item_in_img_upload_path(instance, filename):  # 입고 관리 이미지 경로
    return os.path.join('item_in_img', filename)


def item_out_img_upload_path(instance, filename):  # 출고 관리 이미지 경로
    return os.path.join('item_out_img', filename)


def item_add_qrcode_upload_path(instance, filename):
    return os.path.join('item_add_qrcode', filename)


class EnterpriseMaster(models.Model):
    class Meta:
        unique_together = ('code', 'name')

    code = models.CharField(max_length=128, unique=True, verbose_name='업체코드')
    name = models.CharField(max_length=20, unique=True, verbose_name='업체명')
    manage = models.CharField(max_length=20, null=True, verbose_name='관리명')

    # permissions = models.BigIntegerField(verbose_name='권한')
    permissions = models.CharField(max_length=100, null=True, verbose_name='권한')
    licensee_number = models.CharField(max_length=50, null=False, verbose_name='사업자 번호')
    corporation_number = models.CharField(max_length=50, null=True, verbose_name='법인 등록 번호')
    owner_name = models.CharField(max_length=20, null=True, verbose_name='대표자')
    business_conditions = models.CharField(max_length=50, null=True, verbose_name='업종')
    business_event = models.CharField(max_length=20, null=True, verbose_name='업태')
    postal_code = models.CharField(max_length=128, null=True, verbose_name='우편번호')
    address = models.CharField(max_length=128, null=True, verbose_name='주소')
    email = models.CharField(max_length=36, null=True, verbose_name='이메일')
    office_phone = models.CharField(max_length=36, null=True, verbose_name='대표 전화')
    office_fax = models.CharField(max_length=36, null=True, verbose_name='팩스')
    sign = models.FileField(upload_to=sign_upload_path, default=None, null=True, verbose_name='날인')
    logo = models.FileField(upload_to=logo_upload_path, default=None, null=True, verbose_name='로고')
    certificate = models.FileField(upload_to=business_certificate_upload_path, default=None, null=True, verbose_name='사업자등록증')
    in_or_cor = models.CharField(max_length=1, default=1, null=False, verbose_name='개인사업자 혹은 법인사업자')
    local_or_foreign = models.CharField(max_length=1, default=1, null=False, verbose_name='내국인 혹은 외국인')
    start_up_date = models.DateField(null=True, verbose_name='창립일')
    delete_flag = models.CharField(max_length=1, default='N', null=False, verbose_name='삭제여부')  # N: 삭제안함, Y: 삭제
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateTimeField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='enterprise_created_by',
                                   verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='enterprise_updated_by',
                                   verbose_name='최종작성자')  # 최종작성자


class GroupCodeMaster(models.Model):
    class Meta:
        unique_together = ('enterprise', 'code')

    # code = models.IntegerField(verbose_name='그룹코드')
    code = models.CharField(max_length=10, verbose_name='그룹코드')
    name = models.CharField(max_length=16, verbose_name='그룹코드 이름')
    enable = models.BooleanField(default=True, verbose_name='사용구분')
    description = models.CharField(max_length=128, null=True, verbose_name='설명')
    delete_flag = models.CharField(max_length=1, default='N', null=False, verbose_name='삭제여부')  # N: 삭제안함, Y: 삭제
    created_by = models.ForeignKey('UserMaster',
                                   models.SET_NULL, null=True,
                                   related_name='group_code_master_created_by',
                                   verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster',
                                   models.SET_NULL, null=True,
                                   related_name='group_code_master_updated_by',
                                   verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='group_code_master_enterprise',
                                   verbose_name='업체')


class CodeMaster(models.Model):
    class Meta:
        unique_together = ('enterprise', 'group', 'code')

    group = models.ForeignKey('GroupCodeMaster', models.PROTECT, related_name='codemaster_group',
                              verbose_name='그룹 코드')
    # code = models.IntegerField(verbose_name='상세 코드')  # 상세 코드
    code = models.CharField(max_length=10, verbose_name='상세 코드')  # 상세 코드
    name = models.CharField(max_length=16, verbose_name='상세 코드명')  # 상세 코드명
    ref_code = models.ForeignKey('CodeMaster',
                                 models.PROTECT,
                                 null=True,
                                 related_name='codemaster_ref_detail_code',
                                 verbose_name='참조 상세코드')
    explain = models.CharField(max_length=32, null=True, verbose_name='코드설명')  # 코드설명
    enable = models.BooleanField(default=True, verbose_name='사용구분')  # 사용 구분
    etc = models.CharField(max_length=64, null=True, verbose_name='기타')  # 기 타

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='code_master_created_by',
                                   verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='code_master_updated_by',
                                   verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='code_master_enterprise',
                                   verbose_name='업체')

    def __str__(self):
        return self.name


class UserMaster(AbstractBaseUser, PermissionsMixin):
    class UserMasterManager(BaseUserManager):

        def usermodel(self, user_id, password, username):
            # Do not add user using this usermodel()
            # This is for bootstrapping function

            user = self.model(user_id=user_id,
                              code="00000000",
                              username=username, )

            user.set_password(password)
            return user

        def create_user(self, user_id, password, username=""):
            user = self.usermodel(user_id, password, username)
            user.save(using=self._db)
            return user

        def create_superuser(self, user_id, password, username=""):
            user = self.usermodel(user_id, password, username)
            user.is_superuser = True
            user.save(using=self._db)

            return user

    class Meta:
        unique_together = ('enterprise', 'code')

    objects = UserMasterManager()
    USERNAME_FIELD = 'user_id'

    USER_TYPE_CHOICES = (
        ('Admin', '관리자'),
        ('Member', '멤버'),
        ('Viewer', '뷰어'),
    )

    user_id = models.CharField(max_length=32, unique=True, verbose_name='유저 ID')
    code = models.CharField(max_length=8, null=True, verbose_name='사번')  # 사번
    username = models.CharField(max_length=26, null=True, verbose_name='유저 이름')
    factory_classification = models.ForeignKey('CodeMaster', models.PROTECT,
                                               null=True,
                                               related_name='factory_classification',
                                               verbose_name='공장구분')  # 공장구분,
    employment_division = models.ForeignKey('CodeMaster', models.PROTECT,
                                            null=True,
                                            related_name='employment_division',
                                            verbose_name='고용구분')  # 고용구분,
    employment_date = models.DateField(null=True, verbose_name='입사일자')  # 입사일자
    job_position = models.ForeignKey('CodeMaster', models.PROTECT,
                                     null=True,
                                     related_name='job_position',
                                     verbose_name='직위')
    department_position = models.ForeignKey('CodeMaster', models.PROTECT,
                                            null=True,
                                            related_name='department_position',
                                            verbose_name='부서구분')
    postal_code = models.CharField(max_length=12, null=True, verbose_name='우편번호')  # 우편번호
    address = models.CharField(max_length=64, null=True, verbose_name='주소')  # 주소
    # enable = models.BooleanField(default=True, verbose_name='사용구분')  # 사용구분
    etc = models.CharField(max_length=36, null=True, verbose_name='기타')  # 기타

    email = models.CharField(max_length=36, null=True, verbose_name='이메일')  #
    tel = models.CharField(max_length=36, null=True, verbose_name='전화번호')  #

    is_master = models.BooleanField(default=False, verbose_name='마스터 아이디')

    # permissions = models.BigIntegerField(default=0, verbose_name='권한')
    # permissions = models.CharField(default='0', max_length=100, verbose_name='권한')

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='user_created_by',
                                   verbose_name='최초작성자')  # 최초작성자
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, default=100, related_name='user_master_enterprise',
                                   verbose_name='업체', null=False)
    auth = models.CharField(max_length=10, null=False, default="Viewer", choices=USER_TYPE_CHOICES, verbose_name="권한")
    del_flag = models.CharField(max_length=1, default='N', verbose_name='삭제여부')

    def __str__(self):
        return self.username


class MenuMaster(models.Model):
    code = models.CharField(max_length=50, null=False, verbose_name='메뉴코드')
    name = models.CharField(max_length=50, null=False, verbose_name='메뉴이름')
    path = models.CharField(max_length=256, null=False, verbose_name='경로')
    type = models.CharField(max_length=1, null=False, verbose_name='유형')
    comment = models.CharField(max_length=256, null=True, verbose_name='코멘트')
    i_class = models.CharField(max_length=64, null=True, verbose_name='class icon')
    created_by = models.ForeignKey('UserMaster', on_delete=models.DO_NOTHING, null=True, verbose_name='최초작성자',
                                   related_name='menumaster_created_by')
    updated_by = models.ForeignKey('UserMaster', on_delete=models.DO_NOTHING, null=True, verbose_name='최종작성자',
                                   related_name='menumaster_updated_by')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='최초작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='최종작성일')
    del_flag = models.CharField(max_length=1, default='N', verbose_name='삭제여부')


class Menu_Auth(models.Model):
    menu = models.ForeignKey('MenuMaster', on_delete=models.DO_NOTHING, null=False, verbose_name='메뉴아이디',
                             related_name='menuauth')
    alias = models.CharField(max_length=64, null=True, verbose_name='별칭')
    #enterprise = models.ForeignKey('EnterpriseMaster', on_delete=models.DO_NOTHING, verbose_name='업체')
    user = models.ForeignKey('UserMaster', on_delete=models.DO_NOTHING, null=True, verbose_name='사용자')
    # parent_id = models.IntegerField(null=True, verbose_name='상위클래스')
    #parent = models.ForeignKey('Menu_Auth', on_delete=models.SET_NULL, null=True, verbose_name='상위클래스')
    parent = models.ForeignKey('MenuMaster', on_delete=models.SET_NULL, null=True, verbose_name='상위클래스')
    order = models.IntegerField(null=False, verbose_name='순서')
    use_flag = models.CharField(max_length=1, default='Y', verbose_name='사용여부')
    created_by = models.ForeignKey('UserMaster', on_delete=models.DO_NOTHING, null=True, verbose_name='최초작성자',
                                   related_name='menuauth_created_by')
    updated_by = models.ForeignKey('UserMaster', on_delete=models.DO_NOTHING, null=True, verbose_name='최종작성자',
                                   related_name='menuauth_updated_by')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='최초작성일')
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name='최종작성일')
    del_flag = models.CharField(max_length=1, default='N', verbose_name='삭제여부')


class ColumnMaster(models.Model):
    menu = models.ForeignKey('MenuMaster', on_delete=models.DO_NOTHING, null=False, verbose_name='메뉴아이디',
                             related_name='column')
    label = models.CharField(max_length=64, null=True, verbose_name='컬럼명')
    label_en = models.CharField(max_length=64, null=True, verbose_name='컬럼명(영)')
    pre_label = models.CharField(max_length=128, null=True, verbose_name='선행자')
    tag = models.CharField(max_length=128, null=True, verbose_name='tag')
    type = models.CharField(max_length=64, null=True, verbose_name='text')
    class_name = models.CharField(max_length=128, null=True, verbose_name='class')
    event = models.CharField(max_length=128, null=True, verbose_name='onclick')
    position = models.IntegerField(null=False, verbose_name='순서')
    user = models.ForeignKey('UserMaster', on_delete=models.DO_NOTHING, null=False, verbose_name='사용자')
    use_flag = models.BooleanField(default=True, verbose_name='사용여부')
    visual_flag = models.BooleanField(default=True, verbose_name='표시여부')
    excel_flag = models.BooleanField(default=True, verbose_name='엑셀다운로드사용여부')
    edit_flag = models.BooleanField(default=True, verbose_name='수정필드')
    created_by = models.ForeignKey('UserMaster', on_delete=models.DO_NOTHING, null=True, verbose_name='최초작성자',
                                   related_name='column_created_by')
    updated_by = models.ForeignKey('UserMaster', on_delete=models.SET_NULL, null=True, verbose_name='최종작성자',
                                   related_name='column_updated_by')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='최초작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='최종작성일')
    attr = models.CharField(max_length=64, null=True, verbose_name='속성')
    tier = models.CharField(max_length=1, null=False, default='M', verbose_name='테이블계층')  # 메인과 sub테이블 구분 M,S


class ItemMaster(models.Model):
    ITEM_TYPE_CHOICES = [
        ('P', '제품'),
        ('S', '반제품'),
        ('R', '원재료'),
        ('M', '부재료'),
        ('O', '기타'),
    ]

    item_code = models.CharField(max_length=255, unique=True, null=True, verbose_name='품번')
    item_name = models.CharField(max_length=255, null=True, verbose_name='품명')
    item_detail = models.CharField(max_length=255, null=True, verbose_name='품명상세')
    standard = models.CharField(max_length=255, null=True, verbose_name='규격')
    model = models.CharField(max_length=255, null=True, verbose_name='모델')
    unitname = models.CharField(max_length=255, null=True, verbose_name='단위')
    mass = models.CharField(max_length=255, null=True, verbose_name='무게_질량')
    color = models.CharField(max_length=255, null=True, verbose_name='색상')
    item_type = models.CharField(max_length=1, null=True, choices=ITEM_TYPE_CHOICES, verbose_name='품목 유형')  # ITEM_TYPE_CHOICES
    item_category = models.CharField(max_length=255, null=True, verbose_name='카테고리')
    current_quan = models.FloatField(null=True, default=0, verbose_name='현 재고')
    safe_quan = models.FloatField(null=True, verbose_name='안전 재고')
    qr_code = models.FileField(upload_to=item_add_qrcode_upload_path, default=None, null=True, verbose_name='QR 코드')
    item_image = models.FileField(upload_to=item_master_img_upload_path, default=None, null=True, verbose_name='품목 이미지')
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, default=1, related_name='item_master_enterprise',
                                   verbose_name='업체', null=False)
    del_flag = models.CharField(max_length=1, default='N', verbose_name='삭제여부')
    created_by = models.ForeignKey('UserMaster', on_delete=models.DO_NOTHING, null=False, verbose_name='최초작성자',
                                   related_name='item_created_by')
    updated_by = models.ForeignKey('UserMaster', on_delete=models.SET_NULL, null=True, verbose_name='최종작성자',
                                   related_name='item_updated_by')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='최초작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='최종작성일')


class Warehouse(models.Model):
    code = models.CharField(max_length=255, null=True, verbose_name='창고 코드')
    name = models.CharField(max_length=255, null=True, verbose_name='창고 이름')
    region = models.CharField(max_length=64, null=True, verbose_name='창고 지역')
    wish_flag = models.BooleanField(null=False, default=False, verbose_name='즐겨찾기')
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, default=1, related_name='warehouse_enterprise',
                                   verbose_name='업체', null=False)
    del_flag = models.CharField(max_length=1, default='N', verbose_name='삭제여부')
    created_by = models.ForeignKey('UserMaster', on_delete=models.DO_NOTHING, null=False, verbose_name='최초작성자',
                                   related_name='warehouse_created_by')
    updated_by = models.ForeignKey('UserMaster', on_delete=models.SET_NULL, null=True, verbose_name='최종작성자',
                                   related_name='warehouse_updated_by')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='최초작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='최종작성일')


class WarehouseRack(models.Model):
    rack_code = models.CharField(max_length=128, null=True, verbose_name='랙 코드')
    rack_name = models.CharField(max_length=128, null=True, verbose_name='랙 명')
    rack_row = models.IntegerField(null=True, verbose_name='행')
    rack_line = models.IntegerField(null=True, verbose_name='열')
    wr_etc = models.CharField(max_length=255, null=True, verbose_name='기타 메모')
    warehouse = models.ForeignKey('Warehouse', on_delete=models.DO_NOTHING, null=False, verbose_name='창고',
                                  related_name='warehouse_rack')
    del_flag = models.CharField(max_length=1, default='N', verbose_name='삭제여부')
    created_by = models.ForeignKey('UserMaster', on_delete=models.DO_NOTHING, null=False, verbose_name='최초작성자',
                                   related_name='rack_created_by')
    updated_by = models.ForeignKey('UserMaster', on_delete=models.SET_NULL, null=True, verbose_name='최종작성자',
                                   related_name='rack_updated_by')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='최초작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='최종작성일')


class UnitPrice(models.Model):
    UNIT_TYPE_CHOICES = [
        ('P', '구매'),
        ('S', '판매')
    ]

    unit_price = models.IntegerField(null=True, verbose_name='단가')
    unit_type = models.CharField(max_length=1, null=True, choices=UNIT_TYPE_CHOICES, verbose_name='구분')  # UNIT_TYPE_CHOICES
    fee_rate = models.IntegerField(null=True, verbose_name='수수료')
    u_item = models.ForeignKey('ItemMaster', on_delete=models.DO_NOTHING, null=False, verbose_name='품목정보',
                               related_name='unit_prise_item', )
    # u_custom = models.ForeignKey('CustomMaster', on_delete=models.DO_NOTHING, null=False, verbose_name='거래처 정보',
    #                              related_name='unit_prise_custom')
    etc = models.CharField(max_length=255, null=True, verbose_name='기타 메모')
    del_flag = models.CharField(max_length=1, default='N', verbose_name='삭제여부')
    created_by = models.ForeignKey('UserMaster', on_delete=models.DO_NOTHING, null=False, verbose_name='최초작성자',
                                   related_name='uprice_created_by')
    updated_by = models.ForeignKey('UserMaster', on_delete=models.SET_NULL, null=True, verbose_name='최종작성자',
                                   related_name='uprice_updated_by')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='최초작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='최종작성일')


class ItemIn(models.Model):
    IN_TYPE_CHOICES = [
        ('P', '구매 입고'),
        ('M', '생산 입고'),
        ('C', '재고 조정'),
    ]

    IN_STATUS_CHOICES = [
        ('F', '입고 완료'),
        ('P', '부분 입고'),
        ('W', '입고 대기'),
        ('C', '입고 취소'),
    ]

    in_no = models.CharField(max_length=64, null=True, verbose_name='입고 번호')
    in_type = models.CharField(max_length=1, null=True, choices=IN_TYPE_CHOICES, verbose_name='구분')  # IN_TYPE_CHOICES
    in_status = models.CharField(max_length=1, null=True, choices=IN_STATUS_CHOICES, verbose_name='상태')  # IN_STATUS_CHOICES
    due_date = models.DateTimeField(null=True, verbose_name='입고 예정일')
    in_at = models.DateTimeField(null=True, verbose_name='입고일')
    in_quan = models.FloatField(null=True, verbose_name='수량')
    in_note = models.CharField(max_length=255, null=True, verbose_name='메모')
    in_image = models.FileField(upload_to=item_in_img_upload_path, default=None, null=True, verbose_name='품목 이미지')
    in_item = models.ForeignKey('ItemMaster', on_delete=models.DO_NOTHING, null=False, verbose_name='품목 정보',
                                related_name='item_in_item')
    wh = models.ForeignKey('Warehouse', on_delete=models.DO_NOTHING, null=False, verbose_name='창고 정보',
                                related_name='item_in_warehouse')
    wr = models.ForeignKey('WarehouseRack', on_delete=models.DO_NOTHING, null=False, verbose_name='위치 정보',
                                related_name='item_in_rack')
    uprice = models.ForeignKey('UnitPrice', on_delete=models.DO_NOTHING, null=False, verbose_name='단가 정보',
                                related_name='item_in_price')
    in_custom = models.ForeignKey('CustomerMaster', on_delete=models.DO_NOTHING, default=1, null=False, verbose_name='입고처 정보',
                                   related_name='item_in_custom')  # 구매처(공급사), 판매처(고객사)
    del_flag = models.CharField(max_length=1, default='N', verbose_name='삭제여부')
    created_by = models.ForeignKey('UserMaster', on_delete=models.DO_NOTHING, null=False, verbose_name='최초작성자',
                                   related_name='item_in_created_by')
    updated_by = models.ForeignKey('UserMaster', on_delete=models.SET_NULL, null=True, verbose_name='최종작성자',
                                   related_name='item_in_updated_by')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='최초작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='최종작성일')


class ItemInSub(models.Model):  # 부분 입고 시 사용
    in_at_sub = models.DateTimeField(null=True, verbose_name='입고일')
    in_quan_sub = models.FloatField(null=True, verbose_name='입고 수량')
    in_etc_sub = models.CharField(max_length=255, null=True, verbose_name='특이 사항')
    in_item = models.ForeignKey('ItemIn', on_delete=models.DO_NOTHING, null=False, verbose_name='입고 관리 정보',
                                related_name='sub_item_in')
    del_flag = models.CharField(max_length=1, default='N', verbose_name='삭제여부')
    created_by = models.ForeignKey('UserMaster', on_delete=models.DO_NOTHING, null=False, verbose_name='최초작성자',
                                   related_name='item_sub_created_by')
    updated_by = models.ForeignKey('UserMaster', on_delete=models.SET_NULL, null=True, verbose_name='최종작성자',
                                   related_name='item_sub_updated_by')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='최초작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='최종작성일')


class ItemOut(models.Model):
    OUT_TYPE_CHOICES = [
        ('P', '구매'),
        ('M', '생산'),
        ('C', '재고 조정'),
    ]

    OUT_STATUS_CHOICES = [
        ('F', '입고 완료'),
        ('P', '부분 입고'),
        ('W', '입고 대기'),
        ('C', '입고 취소'),
    ]

    out_no = models.CharField(max_length=64, null=True, verbose_name='출고 번호')
    out_type = models.CharField(max_length=1, null=True, choices=OUT_TYPE_CHOICES, verbose_name='속성')  # OUT_TYPE_CHOICES
    out_status = models.CharField(max_length=1, null=True, choices=OUT_STATUS_CHOICES, verbose_name='상태')  # OUT_STATUS_CHOICES
    out_date = models.DateTimeField(null=True, verbose_name='출고 예정일')
    out_at = models.DateTimeField(null=True, verbose_name='출고일')
    out_quan = models.FloatField(null=True, verbose_name='수량')
    out_note = models.CharField(max_length=255, null=True, verbose_name='메모')
    out_image = models.FileField(upload_to=item_out_img_upload_path, default=None, null=True, verbose_name='품목 이미지')
    out_item = models.ForeignKey('ItemMaster', on_delete=models.DO_NOTHING, null=False, verbose_name='품목 정보',
                                related_name='item_out_item')
    out_wh = models.ForeignKey('Warehouse', on_delete=models.DO_NOTHING, null=False, verbose_name='창고 정보',
                           related_name='item_out_warehouse')
    out_wr = models.ForeignKey('WarehouseRack', on_delete=models.DO_NOTHING, null=False, verbose_name='위치 정보',
                           related_name='item_out_rack')
    out_uprice = models.ForeignKey('UnitPrice', on_delete=models.DO_NOTHING, null=False, verbose_name='단가 정보',
                               related_name='item_out_price')
    out_custom = models.ForeignKey('CustomerMaster', on_delete=models.DO_NOTHING, default=1, null=False, verbose_name='입고처 정보',
                                   related_name='out_price_custom')  # 구매처(공급사), 판매처(고객사)
    del_flag = models.CharField(max_length=1, default='N', verbose_name='삭제여부')
    created_by = models.ForeignKey('UserMaster', on_delete=models.DO_NOTHING, null=False, verbose_name='최초작성자',
                                   related_name='item_out_created_by')
    updated_by = models.ForeignKey('UserMaster', on_delete=models.SET_NULL, null=True, verbose_name='최종작성자',
                                   related_name='item_out_updated_by')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='최초작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='최종작성일')


class ItemOutSub(models.Model):  # 부분 입고 시 사용
    out_at_sub = models.DateTimeField(null=True, verbose_name='출고일')
    out_quan_sub = models.FloatField(null=True, verbose_name='출고 수량')
    out_etc_sub = models.CharField(max_length=255, null=True, verbose_name='특이 사항')
    out_item = models.ForeignKey('ItemOut', on_delete=models.DO_NOTHING, null=False, verbose_name='입고 관리 정보',
                                related_name='sub_item_out')
    del_flag = models.CharField(max_length=1, default='N', verbose_name='삭제여부')
    created_by = models.ForeignKey('UserMaster', on_delete=models.DO_NOTHING, null=False, verbose_name='최초작성자',
                                   related_name='out_sub_created_by')
    updated_by = models.ForeignKey('UserMaster', on_delete=models.SET_NULL, null=True, verbose_name='최종작성자',
                                   related_name='out_sub_updated_by')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='최초작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='최종작성일')


class CustomerMaster(models.Model):
    c_name = models.CharField(max_length=64, null=False, verbose_name='거래처명')
    business_num = models.CharField(max_length=64, null=False, verbose_name='사업자 번호')
    business_type = models.CharField(max_length=12, null=True, verbose_name="업태")
    business_sort = models.CharField(max_length=12, null=True, verbose_name="종목")
    postal_code = models.CharField(max_length=20, null=True, verbose_name='우편번호')
    address = models.CharField(max_length=128, null=True, verbose_name='주소')
    sign = models.FileField(upload_to=sign_upload_path, default=None, null=True, verbose_name='날인')
    logo = models.FileField(upload_to=logo_upload_path, default=None, null=True, verbose_name='로고')
    owner_name = models.CharField(max_length=12, null=False, verbose_name='대표자명')
    official_tel = models.CharField(max_length=20, null=False, verbose_name='대표 전화번호')
    official_fax = models.CharField(max_length=20, null=True, verbose_name='팩스')
    official_email = models.CharField(max_length=36, null=False, verbose_name='대표 이메일')
    manager_tel = models.CharField(max_length=20, null=True, verbose_name='담당자 전화번호')
    manager_email = models.CharField(max_length=36, null=True, verbose_name='담당자 이메일')
    memo = models.CharField(max_length=255, null=True, verbose_name='메모')
    wish_flag = models.BooleanField(null=False, default=False, verbose_name='즐겨찾기')
    del_flag = models.CharField(max_length=1, default='N', verbose_name='삭제여부')
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, default=1, related_name='customer_enterprise',
                                   verbose_name='업체', null=False)
    created_by = models.ForeignKey('UserMaster', on_delete=models.DO_NOTHING, null=False, verbose_name='최초작성자',
                                   related_name='customer_created_by')
    updated_by = models.ForeignKey('UserMaster', on_delete=models.SET_NULL, null=True, verbose_name='최종작성자',
                                   related_name='customer_updated_by')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='최초작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='최종작성일')


class StockStatus(models.Model):
    item = models.ForeignKey('ItemMaster', on_delete=models.DO_NOTHING, null=False, verbose_name='품목 정보',
                                related_name='stock_item')
    io_status = models.CharField(max_length=1, null=False, default='N', verbose_name='입출고 구분')  # I: 입고 O: 출고 N: 오류
    wh = models.ForeignKey('Warehouse', on_delete=models.DO_NOTHING, null=False, verbose_name='창고 정보',
                                related_name='stock_warehouse')
    wr = models.ForeignKey('WarehouseRack', on_delete=models.DO_NOTHING, null=False, verbose_name='위치 정보',
                               related_name='stock_rack')
    input = models.ForeignKey('ItemIn', on_delete=models.DO_NOTHING, null=True, verbose_name='입고서 정보',
                               related_name='stock_in')
    output = models.ForeignKey('ItemOut', on_delete=models.DO_NOTHING, null=True, verbose_name='출고서 정보',
                               related_name='stock_out')
    quantity = models.FloatField(null=True, verbose_name='수량')
    del_flag = models.CharField(max_length=1, default='N', verbose_name='삭제여부')
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, default=1, related_name='stock_enterprise',
                                   verbose_name='업체', null=False)
    created_by = models.ForeignKey('UserMaster', on_delete=models.DO_NOTHING, null=False, verbose_name='최초작성자',
                                   related_name='stock_created_by')
    updated_by = models.ForeignKey('UserMaster', on_delete=models.SET_NULL, null=True, verbose_name='최종작성자',
                                   related_name='stock_updated_by')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='최초작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='최종작성일')


class StockAdjustment(models.Model):
    adjustment_quan = models.FloatField(null=False, default=0, verbose_name="조정 수량")
    adjustment_memo = models.CharField(max_length=255, null=False, verbose_name="조정 사유")
    item = models.ForeignKey('ItemMaster', on_delete=models.DO_NOTHING, null=False, verbose_name='품목 정보',
                                related_name='adjust_item')
    del_flag = models.CharField(max_length=1, default='N', verbose_name='삭제여부')
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, default=1, related_name='adjust_enterprise',
                                   verbose_name='업체', null=False)
    created_by = models.ForeignKey('UserMaster', on_delete=models.DO_NOTHING, null=False, verbose_name='최초작성자',
                                   related_name='adjust_created_by')
    updated_by = models.ForeignKey('UserMaster', on_delete=models.SET_NULL, null=True, verbose_name='최종작성자',
                                   related_name='adjust_updated_by')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='최초작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='최종작성일')
