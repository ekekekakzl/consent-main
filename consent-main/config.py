import os

# --- 로그인 정보 ---
USERNAME = "1"
PASSWORD = "1"

# --- 하드코딩된 기본 설명 (선택적으로 사용) ---
# LLM이 이 기본 설명을 바탕으로 개인화된 설명을 생성합니다.
HARDCODED_BASE_EXPLANATIONS = {
    "수술 필요성": { # <-- 키를 한국어 제목으로 변경
        "_common_explanation": """
        치료를 위해 수술로 암을 제거합니다.
        하지만 암은 주변으로 전이되는 특성이 있어서, 암 조직만 제거하는 것으로는 충분하지 않을 때가 많습니다.

        암세포가 퍼져나갔을 가능성이 있는 자궁 주변 조직이나 림프절도 함께 제거하는 경우가 많습니다.
        림프절은 우리 몸의 면역 체계의 일부인데, 암세포가 림프절을 타고 다른 장기로 전이될 수 있기 때문입니다.
        이렇게 암이 퍼질 위험이 있는 부위까지 함께 제거하여 재발 위험을 낮추는 것이 중요합니다.

        수술로 제거된 조직들은 끝이 아니라, 다음 단계인 병리 검사를 거치게 됩니다.
        병리 검사는 현미경을 통해 제거된 조직들을 아주 자세히 들여다보는 과정으로 암 덩어리가 얼마나 큰지, 암세포가 주변 정상 조직으로 얼마나 깊이 파고들었는지, 림프절에 암세포가 퍼져있는지 확인합니다.

        이 정보들은 앞으로의 치료 계획을 세우는 데 결정적인 역할을 합니다.
        예를 들어, 림프절에 암세포가 발견되었다면, 수술 후 항암 치료나 방사선 치료와 같은 추가 치료가 필요할 수 있습니다.

        최근에는 수술로 얻은 암 조직을 이용해 유전자 변이 검사와 같은 생물학적 표지자 검사를 진행하기도 합니다.
        이 검사를 통해 암이 어떤 유전적인 특징을 가지고 있는지 파악할 수 있습니다.

        이러한 정보들을 바탕으로 환자분에게 가장 효과적이고 개인에게 맞는(맞춤형) 치료 계획을 세울 수 있으며, 이를 통해 치료 효과를 높이고 예후를 더욱 좋게 만들 수 있습니다.
        """,
        "자궁경부암": "_common_explanation", # 공통 설명을 참조하도록 변경
        "난소암": "_common_explanation",     # 공통 설명을 참조하도록 변경
        "자궁내막암": "_common_explanation"
    },
    "수술 방법": { # <-- 키를 한국어 제목으로 변경
        "_common_explanation": """
        수술 방법에 대해 궁금하실 텐데요. 환자분의 수술 전 검사 결과, 현재 건강 상태, 그리고 과거 병력 등을 종합적으로 고려하여 가장 적합한 수술 방법을 결정합니다. 크게 개복 수술, 복강경 수술, 그리고 로봇 수술이 있습니다.
        로봇 수술은 로봇이 직접 수술하는 것이 아니라, 의사가 로봇을 조작하여 수술을 보조하는 장비입니다.
        로봇 수술은 3가지 구성 요소로 구성됩니다:
        수술 콘솔: 의사 선생님이 편안하게 앉아 3D 화면을 보면서 손으로 조작기를 움직여 수술을 진행합니다.
        환자 카트: 4개의 로봇 팔이 달린 본체로, 여기에 카메라와 수술 기구가 장착되어 환자분의 몸 가까이에서 수술을 진행합니다.
        비전 카트: 수술 중 모든 의료진이 큰 화면을 보면서 수술 과정을 함께 확인하고 협력할 수 있게 해주는 장비입니다.

        로봇수술의 방법은 다음과 같습니다:
        작은 절개: 보통 배꼽이나 배꼽 주변에 2cm 정도의 작은 구멍을 내고 '투관침'이라는 기구를 삽입합니다.
        공간 확보: 투관침을 통해 이산화탄소를 주입하여 배를 부풀려 넓은 공간을 만든 후 수술 시야를 확보합니다.
        카메라 및 기구 삽입: 이 구멍으로 카메라를 넣어 배 안을 보면서, 아랫배 쪽에 1cm 정도의 작은 구멍 2개 또는 3개를 더 뚫어 수술 기구를 넣습니다. 이 구멍들의 위치나 개수는 수술 범위에 따라 달라질 수 있습니다.
        조직 제거: 제거할 자궁이나 주변 장기들은 주로 질 쪽을 통해 꺼내거나, 기구를 이용하여 잘게 잘라 꺼냅니다.
        봉합: 마지막으로 질과 배에 낸 구멍들을 꼼꼼하게 봉합합니다.

        로봇 수술의 장점과 단점
        로봇 수술의 장점은 다음과 갑습니다:
        작은 흉터: 개복 수술처럼 크게 절개하지 않아 흉터가 눈에 잘 띄지 않습니다.
        적은 통증: 작은 절개 덕분에 수술 후 통증이 덜합니다.
        빠른 회복: 몸에 부담이 적어 회복 속도가 빠르고 입원 기간도 단축될 수 있습니다.
        적은 합병증 위험: 정교한 수술이 가능하여 합병증 발생 위험을 줄일 수 있습니다.
        더욱 정밀한 수술: 의사 선생님의 손처럼 로봇 팔이 정교하게 움직이고, 미세한 손떨림까지 보정해줍니다. 또한, 10배까지 확대되는 3차원 영상을 보면서 매우 정밀한 수술이 가능합니다.

        하지만 로봇 수술에도 단점은 있습니다:
        비싼 비용: 안타깝게도 아직은 건강보험 적용이 되지 않아 수술 비용 부담이 클 수 있습니다.
        추가적인 준비 시간: 수술 전 로봇 장비를 설치하고 세팅하는 데 추가적인 시간이 소요됩니다.
        제한적인 촉각: 의사 선생님이 직접 손으로 만지는 것만큼 촉각적인 느낌을 느끼기 어렵습니다.
        응급 상황 대비: 드물지만 수술 중 예상치 못한 문제가 발생하면 복강경 수술이나 개복 수술로 전환해야 할 수 있으며, 응급 수술에는 적합하지 않습니다.

        수술 당일 과정과 시간
        수술 당일에는 다음과 같은 과정을 거치게 됩니다.
        수술 대기실 이동: 병실에서 수술 대기실로 이동하여 환자분 신원 등을 다시 한번 확인합니다.
        수술실 이동 및 최종 확인: 수술실로 옮겨져 수술 내용과 환자분 정보를 다시 한번 꼼꼼히 확인합니다.
        마취 및 수술 시작: 전신 마취가 시작되면 수술을 진행합니다.
        회복실 이동: 수술이 끝나면 마취에서 깨어나 회복실로 옮겨져 몸 상태가 안정될 때까지 의료진의 관찰을 받습니다.
        병실 복귀: 상태가 안정적이라고 판단되면 다시 병실로 돌아오게 됩니다.

        수술 시간은 수술 범위, 수술실 내 추가 검사 여부, 그리고 환자분의 복강 내 유착 정도, 혈관 발달 상태 등에 따라 달라질 수 있습니다. 일반적으로 피부 절개부터 봉합까지 약 2시간 이상이 소요됩니다.
        만약 수술 전 예상보다 병이 많이 진행되었거나 유착이 심한 경우에는 수술 시간이 예상보다 길어질 수 있습니다. 수술 준비 과정과 수술 후 회복실에서 안정되는 시간까지 모두 고려한다면, 병실로 다시 돌아오기까지는 약 6시간 이상이 걸릴 수 있습니다. 환자분의 상태에 따라 수술 시간이 더 길어지거나, 정확한 시간을 예측하기 어려운 경우도 있을 수 있으니 이 점 참고해 주시기 바랍니다.
        """,
        "자궁경부암": {
            "base_explanation": "_common_explanation",
            "additional_explanation": """
            자궁경부암 수술은 암의 크기와 위치, 그리고 환자분의 상황에 따라 수술 범위가 달라집니다.
            A형 자궁절제술: 암이 비교적 작을 때 선택하는 수술입니다. 자궁 주변 조직을 최소한으로 제거하고, 질의 위쪽 부분도 1cm 미만으로만 잘라냅니다. 암 조직만 정교하게 제거하여 불필요한 절제를 줄이는 방법입니다.
            B형 자궁절제술: A형보다 암이 조금 더 진행되었을 때 고려합니다. 자궁 외에도 자궁 주변 조직 중 요관 터널 바깥쪽 위치까지 좀 더 넓게 제거하고, 질 위쪽 부분도 1cm 이상 잘라냅니다.
            C형 자궁절제술: 암이 비교적 넓게 퍼져 있거나 깊이 침범했을 때 시행하는 수술입니다. 요관(신장에서 방광으로 소변을 운반하는 관)을 조심스럽게 분리하여 암이 퍼져나갔을 가능성이 있는 광범위한 자궁 주변 조직과 질 위쪽 부분 2cm 이상을 제거합니다. 가장 넓은 범위의 자궁 절제술이라고 할 수 있습니다.
            이와 함께 암세포가 퍼졌을 가능성이 있는 골반 및 대동맥 주변 림프절도 함께 제거하는 것이 일반적입니다. 림프절은 암세포의 전이 경로가 될 수 있기 때문입니다.

            만약 치료 후 임신을 계획하고 있다면, 자궁을 완전히 절제하는 대신 다른 수술 방법을 고려할 수 있습니다. 
            하지만 이는 암의 재발 위험성이나 수술 후 발생할 수 있는 부작용에 대해 의료진과 충분히 상의한 후에 결정됩니다.
            자궁경부 원추절제술: 암이 자궁경부에 국한되어 있고 크기가 매우 작을 때 시행합니다. 자궁경부의 일부를 원뿔 모양으로 잘라내는 수술로, 자궁 전체를 보존할 수 있습니다.
            광범위 자궁경부절제술: 자궁경부 원추절제술보다는 넓지만, 자궁 전체를 절제하는 것보다는 보존적인 방법입니다. 자궁경부와 그 주변 일부 조직을 제거하면서도 자궁 본체를 남겨 임신 가능성을 유지할 수 있습니다.
            """
        },
        "난소암": {
            "base_explanation": "_common_explanation",
            "additional_explanation": """
            난소암, 난관암은 암세포가 배 안의 여러 장기로 퍼져나갈 수 있는 특징이 있습니다. 그래서 수술은 단순히 암 덩어리만 제거하는 것을 넘어, 퍼져나간 암세포까지 최대한 많이 제거하는 것이 매우 중요합니다. 남아있는 암세포가 적을수록 치료 효과가 더 좋기 때문입니다.
            암이 퍼진 정도에 따라 의료진은 아래와 같은 수술들을 복합적으로 진행할 수 있습니다.

            자궁절제술: 암이 자궁으로 퍼졌거나 퍼질 위험이 있을 때, 자궁을 제거하는 수술입니다.
            복강내 복수 또는 세척 세포 검사: 배 안에 고인 물(복수)을 채취하거나, 생리 식염수로 배 안을 씻어낸 물을 검사하여 암세포가 있는지 확인하는 검사입니다. 수술 중 암의 전이 여부를 판단하는 데 사용됩니다.
            난소난관절제술: 암이 발생한 난소와 난관(나팔관)을 제거하는 수술입니다. 반대쪽 난소와 난관도 함께 제거하는 경우가 많습니다.
            대망절제술: '대망'은 위와 대장 사이에 있는 그물 같은 지방 조직인데, 난소암이 잘 전이되는 부위 중 하나입니다. 암이 퍼져있을 가능성이 높으므로 함께 제거합니다.
            골반 림프절 절제술 또는 생검: 골반 주변의 림프절(면역기관)에 암세포가 퍼졌는지 확인하고, 퍼져있다면 제거하는 수술입니다. 암세포가 있는 것으로 의심될 때 조직 일부를 떼어내 검사(생검)할 수도 있습니다.
            복강 복막 절제 또는 생검: '복막'은 배 안의 장기들을 덮고 있는 얇은 막입니다. 난소암은 이 복막을 타고 광범위하게 퍼지는 경우가 많습니다. 암이 있는 복막을 제거하거나, 의심되는 부위의 조직을 떼어내 검사(생검)합니다.
            의심 부위에 대한 절제 또는 생검: 수술 중 암이 퍼진 것으로 의심되는 다른 부위가 있다면, 해당 부위의 암 덩어리를 잘라내거나 조직을 떼어내 검사(생검)하여 암세포 유무를 확인하고 제거합니다.

            암 전이가 심할 경우 추가적으로
            대장 또는 소장 절제술: 암이 대장이나 소장으로 퍼진 경우, 해당 장기의 일부를 제거하는 수술입니다.
            대동맥주위 림프절 절제술 또는 생검: 대동맥 주변의 림프절에 암세포가 전이되었을 때, 이 림프절을 제거하거나 조직을 떼어내 검사(생검)합니다.
            횡격막 복막 절제 또는 생검: '횡격막'은 가슴과 배를 나누는 근육막인데, 이 막을 덮고 있는 복막에 암이 퍼졌을 경우 해당 부위의 복막을 제거하거나 조직을 떼어내 검사(생검)합니다.
            충수돌기 절제술: 맹장 끝에 달린 '충수돌기(맹장염이 생기는 부위)'에 암이 퍼졌거나 퍼질 가능성이 있을 때 제거합니다.
            간 부분 절제: 암이 간으로 퍼진 경우, 간의 일부를 제거하는 수술입니다.
            방광 절제술: 암이 방광으로 침범한 경우, 방광의 일부 또는 전체를 제거하는 수술입니다.
            비장 절제술: '비장(지라)'은 왼쪽 윗배에 있는 장기로, 암이 퍼진 경우 제거할 수 있습니다.
            """
        },
        "자궁내막암": {
            "base_explanation": "_common_explanation",
            "additional_explanation": """
            초기 자궁내막암은 대부분 수술로 치료하게 됩니다. 이때 암의 진행 정도와 환자분의 상황에 따라 수술 범위가 달라질 수 있습니다.

            초기 자궁내막암의 기본적인 수술은 다음과 같습니다.
            골반세척세포검사: 수술 중 배 안을 생리 식염수로 씻어낸 물을 검사하여 암세포가 있는지 확인합니다. 암이 복강 내로 퍼졌는지 알아보는 중요한 검사입니다.
            자궁절제술: 암이 있는 자궁을 제거하는 수술입니다.
            양쪽 난관난소절제술: 자궁과 함께 양쪽 난관(나팔관)과 난소도 함께 제거합니다. 난소암으로의 전이를 막고, 난소에서 분비되는 호르몬이 자궁내막암에 영향을 줄 수 있기 때문입니다.

            젊은 환자분들 중에서 난소 보존을 원하고 임신 계획이 있다면, 의료진은 환자분의 나이와 암의 재발 위험성 등을 종합적으로 고려하여 난소를 보존하는 수술을 시행할 수도 있습니다. 
            하지만 이 경우 난소로 암세포가 전이될 가능성이 있고, 이는 치료 결과(예후)에 좋지 않은 영향을 줄 수 있다는 점을 충분히 상의하고 결정하게 됩니다.

            수술 전 검사 결과나 수술 중 의료진이 직접 눈으로 확인했을 때, 림프절로 암이 퍼졌을 가능성이 있다면 림프절 절제술을 시행할 수 있습니다. 림프절은 우리 몸의 면역 체계이지만, 암세포가 전이되는 주요 통로가 될 수 있기 때문입니다.

            림프절 절제 범위:
            모든 림프절 절제: 암이 퍼졌을 가능성이 높다고 판단되면 해당 부위의 모든 림프절을 제거하기도 합니다.
            선택적 림프절 절제: 육안으로 크기가 커지거나 의심스러운 림프절만 선택적으로 제거할 수 있습니다.
            감시 림프절 검사: 최근에는 '감시 림프절'이라는 방법을 통해 암세포가 가장 먼저 도달하는 림프절을 찾아 그 부분만 선택적으로 제거하기도 합니다. 이렇게 하면 불필요한 림프절 절제를 줄여 수술 후 합병증을 줄일 수 있습니다.

            만약 환자분의 건강 상태가 좋지 않아 수술 시간이 길어지면 위험할 수 있다고 판단될 때(예: 심장이나 폐 질환 등), 의료진은 환자의 안전을 위해 병기 설정(암의 진행 정도를 확인하는)을 위한 추가적인 림프절 절제 등을 생략하고 자궁절제술만 시행하여 수술 시간을 줄이기도 합니다. 이는 환자분의 건강을 최우선으로 고려한 결정입니다.
            """
        }
    },
    "고려 사항": { # <-- 키를 한국어 제목으로 변경
        "_common_explanation": """
        환자분의 안전과 성공적인 수술을 위해, 때로는 로봇 수술 대신 개복 수술을 하거나, 로봇 수술 도중에 개복 수술로 변경해야 할 수도 있습니다.
        로봇 수술이 적합하지 않다고 판단되면 처음부터 개복 수술을 계획할 수 있으며, 해당되는 경우는 다음과 같습니다. 
        자궁 외에 다른 부인과 질환이 동반되어 있어 복잡한 수술이 필요한 경우
        종양의 크기가 너무 커서 로봇 수술로 안전하게 제거하기 어려운 경우
        이전에 수술한 경험이 있어 장기들이 심하게 달라붙어(유착) 있는 것이 의심되는 경우
        검사 결과 암일 가능성이 높다고 판단되는 경우

        로봇 수술을 시작했지만, 수술 중에 예상치 못한 상황이 발생하면 환자분의 안전을 위해 개복 수술로 전환할 수 있으며, 해당되는 경우는 다음과 같습니다. 
        수술 중 출혈이 심하여 로봇 수술로는 지혈이 어려운 경우
        예상보다 유착이 심하여 주변 장기(소화기관, 비뇨기관 등)가 손상될 위험이 큰 경우

        만약 이런 상황에서 무리하게 로봇 수술을 계속 진행하면,
        수술 및 마취 시간이 너무 길어지며,
        유착으로 인해 주변 장기가 손상될 수 있으며,
        종양 조직을 완전히 제거하기 어려울 수 있으며,
        출혈이 많아지고 합병증이 발생할 가능성이 높아지며,
        수혈을 받거나 감염될 위험이 증가할 수 있습니다.

        수술 중 악성 종양(암)이 강하게 의심되는 소견이 발견되면, 림프절이나 난소 절제술 등을 포함한 진단 목적의 개복 수술을 시행할 수 있습니다. 
        이 경우, 추가 수술을 시작하기 전에 환자 보호자분께 먼저 설명드리고 동의를 받을 예정입니다.
        다만, 수술 중 환자분의 상태가 매우 긴급하여 보호자께 미리 설명하고 동의를 얻을 시간이 없는 경우에는, 의료진의 판단에 따라 수술 방법이나 범위를 변경하여 먼저 수술을 진행할 수 있습니다. 이러한 경우에는 수술이 끝난 후 즉시 변경된 사유와 수술 결과를 환자분 또는 보호자분께 자세히 설명해 드릴 것입니다.
        때로는 수술 중에 소화기나 비뇨기 등 다른 장기로 암이 전이되었거나 손상이 발생한 경우가 발견될 수 있습니다. 이때는 외과, 비뇨의학과 등 해당 분야의 의료진과 협력(협진)하여 추가적인 수술을 진행할 수 있습니다.

        이 경우에도 추가 수술을 시작하기 전에 환자 보호자분께 미리 설명드리고 동의를 받을 예정입니다. 
        하지만 앞서 말씀드린 것과 같이, 수술 중 환자분의 상태가 매우 긴급하여 미리 설명과 동의를 얻을 수 없을 때는 먼저 수술을 진행한 후, 수술이 끝나는 대로 변경된 사유와 결과를 환자분 또는 보호자분께 지체 없이 설명해 드리겠습니다.
        """,
        "자궁경부암": "_common_explanation", # 공통 설명을 참조하도록 변경
        "난소암": "_common_explanation",     # 공통 설명을 참조하도록 변경
        "자궁내막암": "_common_explanation"
    },
    "합병증과 관리": { # <-- 키를 한국어 제목으로 변경
        "_common_explanation": """
        수술 후 발생할 수 있는 합병증과 관리 방법
        수술은 암 치료에 중요하지만, 경우에 따라 여러 가지 예상치 못한 상황, 즉 '합병증'이 발생할 수 있습니다. 너무 걱정하시기보다는 어떤 상황이 생길 수 있는지 미리 알아두고 대처하는 것이 중요합니다.
        1) 로봇 수술 관련 합병증
        로봇 수술을 위해 배에 첫 구멍(투관침 삽입)을 낼 때는 의사 선생님이 안을 직접 볼 수 없는 상태에서 진행되기 때문에, 드물게 위, 장, 큰 혈관, 방광 등에 작은 손상이 생길 수 있습니다. 또한, 이 구멍 주위에 피멍이 들거나, 염증이 생기거나, 나중에 배 밖으로 장기가 밀려 나오는 탈장이 생길 수도 있습니다.
        수술 시 배를 부풀리기 위해 넣는 이산화탄소 가스가 드물게 심장이나 폐 기능에 영향을 주거나, 혈관으로 들어가 혈관을 막는(가스색전증) 위험이 아주 드물게 있습니다. 가스가 횡격막을 자극해서 어깨뼈에 통증이 생길 수 있지만, 대부분 수술 후 24시간 안에 좋아집니다. 또, 가스가 피부 밑으로 스며들어 공기 주머니가 생길 수 있으나, 이것도 대부분 수술 후에 자연스럽게 사라집니다.
        2) 주변 장기 손상
        혹이 주변 장기(방광, 요관, 요도, 큰창자, 작은창자 등)와 너무 가깝거나, 이전에 수술 경험(제왕절개 포함), 자궁내막증, 큰 근종 등이 있어서 장기들이 서로 심하게 달라붙어(유착) 있는 경우에는 수술 중 주변 장기가 손상될 위험이 커질 수 있습니다.
        만약 수술 중에 이런 손상을 발견하면, 해당 장기를 전문으로 하는 다른 과(외과, 비뇨의학과 등) 의료진과 협력하여 바로 치료할 수 있습니다. 하지만 간혹 수술 중에는 발견되지 못하고 수술 후에 감염이나 구멍(누공) 같은 합병증으로 뒤늦게 나타날 수도 있습니다.
        만약 소변 길(요로계)이 손상되었다면 가벼운 경우 소변줄(스텐트)을 삽입하여 회복을 기다릴 수 있지만, 심하면 수술로 고치거나 옆구리에 소변 주머니를 다는 치료가 필요할 수 있습니다. 장이 손상되었다면 개복 수술로 전환하여 손상된 부분을 치료해야 할 수 있으며, 손상 정도에 따라 일시적으로 인공 항문(장루)을 만들 수도 있습니다.
        3) 출혈
        수술 중 피가 많이 나면 수술 중이나 수술 후에 수혈이 필요할 수 있습니다. 만약 큰 혈관이 다치면 예상보다 많은 양의 출혈이 생길 수 있으며, 이때는 혈관외과나 흉부외과 등 해당 전문의의 도움이 필요할 수도 있습니다.
        일반적으로는 혈관을 묶거나, 전기 소작술, 지혈제 사용 등으로 피를 멈추게 하려 노력합니다. 하지만 수술 후에도 계속 피가 나거나 환자분의 상태가 불안정하면, 피를 완전히 멈추기 위해 재수술을 해야 할 수도 있습니다.
        4) 수술 부위 통증
        수술 부위의 통증은 수술 후 2~5일 정도는 비교적 심할 수 있지만, 이후에는 점차 나아집니다. 진통제나 스스로 조절할 수 있는 통증 조절 장치(자가통증조절장치)를 사용하여 통증을 조절해 드립니다.
        5) 혈전 색전증 (피떡으로 인한 문제)
        수술 후에는 다리 등에 피떡(혈전)이 생길 위험이 있습니다. 이 피떡이 혈관을 따라 이동하여 폐, 뇌, 심장, 다리 등으로 가서 혈관을 막는 색전증이 발생할 수 있습니다.
        가벼운 경우 다리가 붓거나 아프고, 숨이 차는 증상이 나타날 수 있지만, 심한 경우 반신마비가 오거나 심하면 심장마비로 사망에 이를 수도 있는 매우 위험한 합병증입니다.
        피떡이 생길 위험이 높은 환자분들께는 수술 전후로 혈액 응고를 막는 약을 사용하거나, 다리에 압박 스타킹을 신겨드려 예방에 힘쓰고 있습니다.
        6) 장폐색 (장이 막히는 것)
        수술 후 장이 서로 달라붙거나(유착) 장 움직임이 일시적으로 줄어들면서 장이 막히는 장폐색이 생길 수 있습니다.
        가벼운 경우 식사를 중단하고 콧줄(비위관)을 삽입하여 증상을 완화할 수 있지만, 심한 경우에는 막힌 장의 일부를 잘라내는 수술이 필요할 수도 있습니다.
        7) 수술 부위 및 기타 감염
        수술 부위에 염증이 생길 수 있으며, 이로 인해 수술 부위가 벌어지거나 탈장이 생길 수도 있습니다. 염증이 생긴 부위를 소독하고 다시 봉합하여 회복되지만, 이로 인해 병원에 더 오래 계셔야 할 수 있습니다.
        소변 길 염증(요로 감염), 폐렴, 혈관 염증(정맥염) 등 다른 부위에도 감염이 생길 수 있으며, 이 경우에도 입원 기간이 길어질 수 있습니다. 만약 배 안에 심한 염증이 생기면 재수술이 필요할 수도 있습니다. 저희는 적절한 예방적 항생제를 사용하여 감염 위험을 줄이려 노력하고 있습니다.
        8) 배뇨 장애 (소변 보는 데 어려움)
        수술 후 일시적으로 방광 기능이 약해져서 소변을 보기가 어려울 수 있습니다. 이 경우 소변줄을 이용하거나 약물 치료를 통해 회복을 돕습니다. 일부 환자분들은 수개월 동안 지속되거나 드물게 영구적으로 소변을 보는 데 어려움을 겪을 수도 있습니다.
        9) 주변 장기와의 누공 (새는 구멍)
        수술 범위가 넓거나 배 안에 심한 유착이 있는 경우, 직장(대변이 모이는 곳)이나 방광 등 주변 장기와 자궁 자리 사이에 비정상적인 구멍(누공)이 생길 수 있습니다. 자궁내막증, 비만, 골반염, 과거 방사선 치료 경험 등이 있으면 누공 위험이 더 높아집니다.
        누공은 수술 직후에 발견될 수도 있지만, 수술 후 몇 주가 지나서 발견될 수도 있습니다. 이 경우 질을 통해 대변이나 소변이 새어 나올 수 있으며, 심한 정도에 따라 추가 수술이 필요할 수 있습니다.
        10) 운동 및 감각 기능 저하
        긴 시간 동안 특정 자세로 수술을 받으면 신경이나 근육이 압박되어 팔다리의 감각이 둔해지거나 움직임이 불편해지는 신경병증이 생길 수 있습니다. 또한, 혹이 크거나 신경 조직과 유착되어 있는 경우 수술 중 어쩔 수 없이 신경이 손상될 수도 있습니다.
        대부분의 경우 일시적으로 발생하며 시간이 지나면서 자연스럽게 회복됩니다. 하지만 간혹 수개월 이상 약물 치료나 재활 치료가 필요할 수 있으며, 드물게는 완전히 회복되지 않고 영구적인 후유증으로 남을 수도 있습니다.
        11) 면역력 약화 (비장 절제술을 한 경우)
        만약 수술 중 비장(지라)이라는 장기를 함께 절제했다면, 일부 세균이나 바이러스 감염에 취약해질 수 있습니다. 하지만 독감, 폐렴구균, 파상풍, 백일해 등 필요한 예방 백신을 접종하면 감염 위험을 크게 줄일 수 있습니다.
        """,
        "자궁경부암": "_common_explanation", # 공통 설명을 참조하도록 변경
        "난소암": "_common_explanation",     # 공통 설명을 참조하도록 변경
        "자궁내막암": "_common_explanation"
    },
    "주의사항": { # <-- 키를 한국어 제목으로 변경
        "_common_explanation": """
        1) 주치의(집도의) 변경 가능성
        수술 과정에서 환자의 상태나 의료기관의 사정에 따라 부득이하게 주치의(집도의)가 변경될 수 있는 상황이 발생할 수 있습니다.
        수술 중 환자분께 응급 상황이 발생하여 다른 전문의의 도움이 필요한 경우
        수술 중 다른 응급 환자가 발생하여 주치의가 긴급하게 자리를 비워야 하는 경우
        주치의의 갑작스러운 질병, 출산 등 피치 못할 개인적인 사유가 발생한 경우
        그 외에 수술을 계속 진행하기 어려운 예상치 못한 상황이 발생한 경우

        이 경우에는, 수술을 시작하기 전에 환자분 또는 보호자분께 변경 사유를 자세히 설명해 드리고 서면 동의를 받을 예정입니다.
        하지만, 수술 도중에 환자분의 상태가 매우 긴급하여 미리 설명하고 동의를 얻을 시간이 없는 경우에는, 환자분의 안전을 최우선으로 하여 주치의를 먼저 변경하여 수술을 진행할 수 있습니다. 
        이러한 경우에는 수술이 끝난 후 즉시 변경 사유와 수술 진행 결과를 환자분 또는 보호자분께 자세히 설명해 드릴 것입니다.

        2) 수술 전, 후 주의사항
        1. 수술 전부터 퇴원까지, 담당 의료진이 안내해 드리는 모든 지시사항을 잘 따라야 합니다.
        2. 혹시 임신 중이거나 임신 가능성이 있다면 반드시 수술 전에 담당 의료진에게 알려주셔야 합니다. 
        수술이나 마취가 태아에게 영향을 줄 수 있기 때문에 임신 가능성이 있다면 수술이나 마취 전에 임신 확인 검사를 먼저 받으셔야 합니다.
        3. 수술 전후로 담당 의료진에게 듣지 못했던 새로운 증상이 나타난다면 지체 없이 알려야 합니다. 
        예를 들어, 갑자기 열이 나거나, 통증이 심해지거나, 평소와 다른 분비물이 나오는 등 몸에 이상이 느껴진다면 바로 말씀해주어야 합니다.
        4. 조영제 (검사 시 사용하는 약물)나 특정 약물에 대해 과민 반응(알레르기)을 경험한 적이 있다면 수술 전에 반드시 담당 의료진에게 알려야 합니다.
        """,
        "자궁경부암": "_common_explanation", # 공통 설명을 참조하도록 변경
        "난소암": "_common_explanation",     # 공통 설명을 참조하도록 변경
        "자궁내막암": "_common_explanation"
    },
    "자기결정권": { # <-- 키를 한국어 제목으로 변경
        "_common_explanation": """
        저는 의료진으로부터 이번 수술(또는 시술, 검사, 마취, 진정요법)의 목적, 기대되는 효과, 진행 과정, 생길 수 있는 부작용이나 합병증 등에 대해 설명을 들었습니다.
        이번 수술(또는 시술, 검사, 마취, 진정요법) 중에는 예상하지 못한 사고가 생길 수 있고, 몸의 특이 체질 때문에 문제가 생길 수도 있다는 설명도 이해했습니다.
        저는 이번 수술(또는 시술, 검사, 마취, 진정요법)에 협조하겠으며, 제 건강 상태에 대해 솔직하게 알리겠습니다. 또, 수술 중 필요한 판단은 의료진에게 맡기겠습니다.
        수술(또는 시술, 검사, 마취, 진정요법) 전에 방법이 바뀔 수도 있고, 범위가 넓어질 수도 있다는 설명을 들었고, 이를 이해했습니다.
        수술(또는 시술, 검사, 마취, 진정요법) 전에, 참여하는 의료진이 바뀔 수도 있다는 점과 그 이유에 대한 설명을 들었고, 이를 알고 있습니다.

        """,
        "자궁경부암": "_common_explanation", # 공통 설명을 참조하도록 변경
        "난소암": "_common_explanation",     # 공통 설명을 참조하도록 변경
        "자궁내막암": "_common_explanation"
    },
}


# --- OX 퀴즈 데이터 ---
QUIZ_DATA = {
    "necessity": [
        {
            "question": "로봇수술 시 암이 전이되지 않도록 림프절을 제거할 수 있어요. (O/X)",
            "answer": "O",
            "explanation": "암은 림프절을 따라 전이되는 성질이 최소 침습 수술이라 상처가 작고, 회복도 빨라요. 정말 잘 이해하셨네요! 😊"
        },
        {
            "question": "로봇수술은 개복이나 복강경보다 수술 시간이 짧다는 장점이 있어요. (O/X)",
            "answer": "X",
            "explanation": "로봇 수술은 수술을 하기 위해 로봇을 준비하는 시간이 추가적으로 소요되어어 무조건 수술시간이 짧아지는 건 아니에요. 💖"
        }
    ],
    "method": [
        {
            "question": "로봇은 의사 선생님이 수술 계획을 입력하면 환자 상태에 맞춰 수술하는 방식이에요. (O/X)",
            "answer": "X",
            "explanation": "로봇이 스스로 수술하는 것이 아니라, 의사 선생님이 원격으로 로봇 팔을 조종하며 수술하는 거예요. 그래도 의사 선생님이 직접 로봇을 움직이니 걱정하지 마세요! 👍"
        },
        {
            "question": "로봇수술은 아주 작은 부위까지 확대해서 볼 수 있고 삼차원으로 볼 수 있어 더 정교하게 수술할 수 있어요. (O/X)",
            "answer": "O",
            "explanation": "로봇에 달린 카메라를 통해 훨씬 더 자세히 볼 수 있게 도와줘서 수술이 더 섬세하게 진행될 수 있어요. ✨"
        }
    ],
    "considerations": [
        {
            "question": "로봇수술 중에 복강경이나 개복 수술을 바뀔 수 있어요. (O/X)",
            "answer": "O",
            "explanation": "수술 중 상황에 따라서 수술 진행상황이 바뀔 수 있어요. 환자분의 안전을 위해 의료진이 최선을 다하고, 잘 대처할 준비가 되어 있으니 너무 걱정 마세요. ✨"
        },
        {
            "question": "로봇수술 중에 다른 조직에 손상이 갈 수도 있어요. (O/X)",
            "answer": "O",
            "explanation": "로봇수술 중 떼어내야 할 조직들이 다른 조직에 딱 붙어 있으면, 떼어내는 과정 중에 불가피하게 다른 조직이 손상될 수 있는 가능성이 있어요. 😊"
        }
    ],
    "side_effects": [
        {
            "question": "로봇 수술은 합병증이 전혀 없으므로 걱정할 필요가 없어요. (O/X)",
            "answer": "X",
            "explanation": "로봇 수술은 아주 작은 확률이라도 합병증이 생길 수 있어요. 하지만 의료진이 합병증을 최소화하기 위해 최선을 다하고, 혹시 생기더라도 잘 대처하면 합병증은 없어질 수 있으니 너무 걱정 마세요. 저희가 함께할 거예요! 💖"
        },
        {
            "question": "수술 후 어지럽거나 수술 부위가 아프면 그냥 참지 말고 의료진에게 바로 알려야 해요. (O/X)",
            "answer": "O",
            "explanation": "불편한 점이 있다면 언제든지 저희에게 이야기해주세요. 환자분의 편안한 회복을 돕는 것이 저희의 역할이랍니다! 🏥"
        }
    ],
    "precautions": [
        {
            "question": "수술 후에는 바로 집으로 돌아가서 하고 싶은 것을 다 해도 괜찮아요. (O/X)",
            "answer": "X",
            "explanation": "수술 후에 너무 힘이 많이 드는 운동 시 수술 부위에 무리가 될 수 있어요. 의료진이 알려주는 회복 기간 동안은 무리하지 않고 충분히 쉬어 몸을 회복하는 것이 중요합니다! 🏥"
        },
        {
            "question": "수술 후에는 가벼운 걷기 운동을 하고 숨을 깊고 천천히 쉬는 운동이이 몸이 회복되는 것을 도와주는 것이 좋아요. (O/X)",
            "answer": "O",
            "explanation": "천천히 몸을 움직여주는 것이 회복에 도움이 돼요. 너무 무리하지 않는 선에서 움직여주세요. 또한 전신마취 후 깊고 천천히 숨을 쉬어서 폐가 쪼그라들지 않도록 예방하는 것이 중요해요. 💪"
        }
    ],
    "self_determination": [
        {
            "question": "수술 동의서에는 수술 후에 발생할 수 있는 모든 가능성을 알려드려야 할 내용이 들어있어야 해요. (O/X)",
            "answer": "O",
            "explanation": "수술 동의서에는 수술 전, 중, 후에 환자에게 발생할 수 있는 긍정적, 부정적 가능성을 모두 포함하는 내용이 담겨있어야 해요! 🫂"
        },
        {
            "question": "수술 동의서의 내용을 모두 이해했는지 확인하고 서명하는 것이 중요해요. (O/X)",
            "answer": "O",
            "explanation": "환자분께서 내용을 정확히 알고 동의하시는 것이 가장 중요하답니다. 혹시라도 궁금한 점이 있다면 언제든지 다시 물어봐주세요. 🤝"
        }
    ],
}

# --- 자주 묻는 질문 데이터 (FAQ) ---
# 각 FAQ 질문에 대한 답변을 추가합니다.
FAQ_DATA = {
    "necessity": [
        {"question": "1. 로봇수술 말고 다른 수술 방법은 없나요?", "answer": "환자분의 상태에 따라 개복 수술이나 복강경 수술 등 다른 수술 방법도 고려될 수 있습니다. 의료진과 충분히 상담하여 가장 적합한 방법을 선택하는 것이 중요합니다."},
        {"question": "2. 로봇수술을 꼭 해야만 하는 건가요?", "answer": "로봇수술은 특정 질환이나 환자 상태에 더 유리한 경우에 권장됩니다. 반드시 로봇수술만 해야 하는 것은 아니며, 의료진이 환자분께 가장 이점이 많은 방법을 제안해 드릴 것입니다."},
        {"question": "3. 만약 수술을 안 하면 어떻게 되나요?", "answer": "수술을 하지 않을 경우 질환의 진행, 증상 악화, 합병증 발생 등 다양한 결과가 있을 수 있습니다. 의료진이 환자분의 현재 상태와 수술하지 않았을 때의 예상 경과에 대해 자세히 설명해 드릴 것입니다."},
    ],
    "method": [
        {"question": "1. 수술 시간은 얼마나 걸리나요?", "answer": "수술 시간은 환자분의 질환 종류, 수술 범위, 개인의 특성에 따라 달라질 수 있습니다. 일반적으로 몇 시간 정도 소요될 수 있으며, 의료진이 예상 시간을 미리 알려드릴 것입니다."},
        {"question": "2. 로봇이 혼자서 수술하는 건가요?", "answer": "아니요, 로봇은 의사 선생님의 정교한 조작을 돕는 도구입니다. 의사 선생님이 로봇 시스템을 통해 수술 기구를 직접 제어하며 수술을 진행합니다. 로봇이 스스로 판단하여 수술하는 것이 아닙니다."},
        {"question": "3. 수술 후 흉터는 얼마나 남나요?", "answer": "로봇수술은 작은 절개를 통해 진행되므로, 개복 수술에 비해 흉터가 훨씬 작습니다. 보통 몇 개의 작은 구멍 자국만 남게 되며, 시간이 지나면서 점차 흐려집니다."},
    ],
    "considerations": [
        {"question": "1. 수술 전에 꼭 준비해야 할 것이 있나요?", "answer": "수술 전에는 의료진의 지시에 따라 금식, 약물 복용 중단, 필요한 검사 진행 등 여러 준비가 필요합니다. 자세한 내용은 수술 전 안내 시 알려드릴 것입니다."},
        {"question": "2. 금식은 왜 해야 하나요?", "answer": "금식은 마취 및 수술 중 발생할 수 있는 흡인성 폐렴 등 합병증을 예방하기 위해 필수적입니다. 위장 내 음식물이 역류하여 기도로 넘어가는 것을 막기 위함입니다."},
        {"question": "3. 수술 전 복용하던 약은 어떻게 해야 하나요?", "answer": "수술 전 복용 중인 모든 약물에 대해 의료진에게 반드시 알려주셔야 합니다. 특히 혈액 응고에 영향을 미치는 약물은 수술 전 일정 기간 중단해야 할 수 있습니다."},
    ],
    "side_effects": [
        {"question": "1. 로봇 수술은 합병증이 전혀 없나요?", "answer": "아니요. 모든 수술은 아주 작은 확률이라도 합병증이 생길 수 있어요. 하지만 의료진이 부작용을 최소화하기 위해 최선을 다하고, 혹시 생기더라도 잘 대처할 준비가 되어 있으니 너무 걱정 마세요. 💖"},
        {"question": "2. 예상치 못한 다른 부작용은 없나요?", "answer": "모든 수술에는 감염, 출혈, 장기 손상, 마취 부작용 등 예상치 못한 합병증의 위험이 있습니다. 의료진이 발생 가능한 모든 부작용에 대해 자세히 설명해 드릴 것입니다."},
        {"question": "3. 합병증이 생기면 어떻게 대처해주시나요?", "answer": "합병증 발생 시 의료진이 신속하게 환자분의 상태를 평가하고 필요한 조치를 취할 것입니다. 최선을 다해 안전하게 대처할 준비가 되어 있습니다."},
    ],
    "precautions": [
        {"question": "1. 수술 후 언제부터 음식을 먹을 수 있나요?", "answer": "수술 후 장 운동 회복 상태에 따라 물부터 시작하여 미음, 죽 등으로 점차 식사를 진행합니다. 의료진의 지시에 따라야 합니다."},
        {"question": "2. 퇴원 후 집에서 주의해야 할 점은 무엇인가요?", "answer": "퇴원 후에는 무리한 활동을 피하고 충분한 휴식을 취해야 합니다. 수술 부위 관리, 약 복용, 통증 조절 등 의료진이 알려드리는 주의사항을 잘 지켜주셔야 합니다."},
        {"question": "3. 언제부터 운동을 다시 시작할 수 있나요?", "answer": "가벼운 걷기 등은 비교적 일찍 시작할 수 있지만, 격렬한 운동은 수술 부위 회복에 따라 점진적으로 시작해야 합니다. 의료진과 상담 후 결정하는 것이 좋습니다."},
    ],
    "self_determination": [
        {"question": "1. 동의서 내용에 대해 언제든 물어볼 수 있나요?", "answer": "네, 동의서 내용에 대해 언제든지 다시 물어보실 수 있습니다. 환자분에게 충분한 설명을 제공하고 서명을 받는 것이 동의서의 용도입니다."},
        {"question": "2. 수술 동의를 철회할 수도 있나요?", "answer": "네, 수술 동의는 수술 전까지 언제든지 철회할 수 있습니다. 동의 철회 의사를 의료진에게 알려주시면 됩니다."},
        {"question": "3. 가족들도 동의서 설명을 함께 들을 수 있나요?", "answer": "네, 환자분이 원하시면 가족분들도 동의서 설명을 함께 들을 수 있습니다. 중요한 결정을 함께 논의하는 데 도움을 드릴 것입니다."},
    ],
}

# 사이드바 섹션 매핑
SECTIONS_SIDEBAR_MAP = {
    "necessity": {"title": "수술 필요성", "idx": 1},
    "method": {"title": "수술 방법", "idx": 2},
    "considerations": {"title": "고려 사항", "idx": 3},
    "side_effects": {"title": "합병증과 관리", "idx": 4},
    "precautions": {"title": "주의사항", "idx": 5},
    "self_determination": {"title": "자기결정권", "idx": 6},
}

# 섹션 순서 (이전/다음 버튼 등에 사용)
SECTIONS_ORDER_KEYS = ["necessity", "method", "considerations", "side_effects", "precautions", "self_determination"]