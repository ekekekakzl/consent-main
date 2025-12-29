import os

# --- 로그인 정보 ---
USERNAME = "1"
PASSWORD = "1"

# 섹션 순서 (이전/다음 버튼 등에 사용)
SECTIONS_ORDER_KEYS = ["necessity", "method", "considerations", "side_effects"]

# 사이드바 섹션 매핑
SECTIONS_SIDEBAR_MAP = {
    "necessity": {"title": "로봇 수술이란?", "idx": 1},
    "method": {"title": "로봇수술의 장점과 단점", "idx": 2},
    "considerations": {"title": "수술은 어떻게 진행되나요?", "idx": 3},
    "side_effects": {"title": "알아두어야할 점", "idx": 4},
}


IMAGE_FILE_MAP = {
    # 수술 종류 1: 로봇보조 자궁절제술
    "로봇보조 자궁절제술": {
        "necessity": "images/gynecologic/necessity.png", 
        "method": "images/gynecologic/method.png",
        "considerations": "images/gynecologic/considerations.png",
        "side_effects": "images/gynecologic/side_effects.png",
    },
    # 수술 종류 2: 로봇보조 전립선절제술
    "로봇보조 전립선절제술": {
        "necessity": "images/urology/necessity.png",
        "method": "images/urology/method.png",
        "considerations": "images/urology/considerations.png",
        "side_effects": "images/urology/side_effects.jpg",
    },
}

HARDCODED_BASE_EXPLANATIONS = {
"로봇 수술이란?": {
    "로봇보조 자궁절제술": 
    
    """
    
    로봇수술은 <mark><span style="color: #007bff;">**세 가지**</span></mark> 장비로 이루어져 있습니다.
    - **콘솔**
    <br>: 의사가 3D 화면을 보며 로봇 팔을 <mark><span style="color: #007bff;">**직접**</span></mark> 조종하여 진행합니다.
    - **환자카트**
    <br>: 카메라와 수술 기구가 달린 <mark><span style="color: #007bff;">**4개의 로봇 팔**</span></mark>이 있습니다.
    - **비전카트**
    <br>: 수술 중 의료진 모두가 <mark><span style="color: #007bff;">**화면을 공유**</span></mark>할 수 있도록 도와줍니다.
        """,

    "로봇보조 전립선절제술": 
    
    """

    로봇수술은 <mark><span style="color: #007bff;">**세 가지**</span></mark> 장비로 이루어져 있습니다.
    - **콘솔**
    <br>: 의사가 3D 화면을 보며 로봇 팔을 <mark><span style="color: #007bff;">**직접**</span></mark> 조종하여 진행합니다.
    - **환자카트**
    <br>: 카메라와 수술 기구가 달린 <mark><span style="color: #007bff;">**4개의 로봇 팔**</span></mark>이 있습니다.
    - **비전카트**
    <br>: 수술 중 의료진 모두가 <mark><span style="color: #007bff;">**화면을 공유**</span></mark>할 수 있도록 도와줍니다.

    """
    },

    "로봇수술의 장점과 단점": {
        "로봇보조 자궁절제술": 
        """

        |<span style="color: #007bff;">**장점**</span>|<span style="color: #dc143c;">**단점**</span>|
        |---|---|
        |상처가 작고 아픔이 적습니다.<br> <span style="color: #007bff;">**회복이 빠릅니다.**</span>|건강보험이 적용되지 않아 <br><span style="color: #dc143c;">**수술비가 비쌉니다.**</span>
        화면을 확대해서 볼 수 있고,<br>로봇 팔이 자유롭게 움직여 <br><span style="color: #007bff;">**정교한 수술**</span>이 가능합니다.|로봇세팅시간이 추가되어<br><span style="color: #dc143c;">**수술 시간이 더**</span> 걸립니다.
        손떨림 없이 <br>미세한 작업이 가능해<br>주변 혈관이나 신경 <span style="color: #007bff;">**손상을 최소화**</span>할 수 있습니다.|수술 중 문제가 생기면 <br><span style="color: #dc143c;">**배를 열거나 복강경 수술로**</span> 바뀔 수 있습니다.|

        """,

        "로봇보조 전립선절제술":

        """

        |<span style="color: #007bff;">**장점**</span>|<span style="color: #dc143c;">**단점**</span>|
        |---|---|
        |상처가 작고 아픔이 적습니다.<br> <span style="color: #007bff;">**회복이 빠릅니다.**</span>|건강보험이 적용되지 않아 <br><span style="color: #dc143c;">**수술비가 비쌉니다.**</span>
        화면을 확대해서 볼 수 있고, <br>로봇 팔이 자유롭게 움직여 <span style="color: #007bff;">**정교한 수술**</span>이 가능합니다.|로봇 세팅 시간이 추가되어<br><span style="color: #dc143c;">**수술 시간이 조금 더**</span> 걸립니다.
        발기 관련 신경을 살리거나 <span style="color: #007bff;">**방광과 요도를 다시 연결**</span>하는 <br>중요한 과정을 더 <span style="color: #007bff;">**정확하게**</span> 할 수 있습니다.|수술 중 문제가 생기면<br><span style="color: #dc143c;">**배를 여는 수술로**</span> 바뀔 수 있습니다.|


        """
    },
    "수술은 어떻게 진행되나요?": {
        "로봇보조 자궁절제술": 
        
        """
        ❶ 배꼽 주변에 2cm 정도의 작은 구멍을 뚫고 관을 넣습니다.
        <br>❷ <mark>**이산화탄소 가스**</mark>를 넣어 배를 부풀려 수술할 공간을 만듭니다.
        <br>❸ 카메라와 수술 도구가 들어갈 0.5-1cm 크기의 구멍을 <br>아랫배에 <mark><span style="color: #dc143c;">**2~3개 더**</span></mark> 뚫습니다.(구멍 위치와 개수는 달라질 수 있습니다.)
        <br>❹ 떼어낸 자궁 등은 질을 통해 꺼내거나, 잘게 잘라서 꺼냅니다.
        <br>❺ 구멍을 뚫었던 부위를 꿰매고 수술을 마칩니다.
        
        |**수술 시간: 2시간**|**총 소요 시간: 6시간**|
        |---|---|
        |환자의 상태나 유착(장기 등이 달라붙는 현상) 정도에 따라 더 길어질 수 있습니다.|수술 준우,           <br><mark><span style="color: #dc143c;">**안전을 위해 배를 여는 수술**</span></mark>로 바꿀 수 있습니다.

        - 다른 장기(소화기관, 비뇨기관 등)에 손상이 생기면, 
        <br><mark><span style="color: #dc143c;">**다른 과 의사와 함께 수술**</span></mark>하며 수술 범위가 커질 수 있습니다.

        - 수술 중 **림프절이나 난소를 함께 제거**할 수도 있습니다.


        """,
        "로봇보조 전립선절제술": """

        ❶ **배를 여는 수술로 바뀔 수 있어요**
        - 수술 중 **장이 심하게 달라붙어 있거나 예상치 못한 문제**로 로봇 수술을 계속하기 어려우면, 
        <br>환자의 안전을 위해 즉시 <mark><span style="color: #dc143c;">**배를 여는 수술(개복수술)로 변경**</span></mark>할 수 있습니다.

        ❷ **수술 후 소변줄을 차고 있어요**
        - 수술 후에는 소변이 잘 빠지도록 <mark><span style="color: #dc143c;">**소변줄(도뇨관)을 며칠간 유지**</span></mark>합니다.
        - 보통 수술 후 5~7일 뒤에 소변이 새지 않는지 확인하고 소변줄을 제거합니다.
        - 소변줄을 뺀 직후에는 자신도 모르게 소변이 샐 수 있으니, 임시로 사용할 <span style="color: #dc143c;">**기저귀를 준비**</span>하는 것이 좋습니다.

        ❸ **추가 치료가 필요할 수 있어요**
        - 수술 후 최종 조직검사 결과에 따라, 또는 나중에 암이 재발하면 방사선 치료나 호르몬 치료를 추가로 받을 수 있습니다.
        - 퇴원 후에도 <mark><span style="color: #dc143c;">**정기적인 피검사(전립선 수치 검사)**</span></mark>를 통해 재발 여부를 계속 확인합니다.

        """
    },
}

# 사이드바 섹션 매핑
SECTIONS_SIDEBAR_MAP = {
    "necessity": {"title": "로봇 수술이란?", "idx": 1},
    "method": {"title": "로봇수술의 장점과 단점", "idx": 2},
    "considerations": {"title": "수술은 어떻게 진행되나요?", "idx": 3},
    "side_effects": {"title": "알아두어야할 점", "idx": 4},
}













