//
//  ScenarioView.swift
//  SwiftUI_MQTT
//
//  Created by 차차 on 11/29/24.
//

import SwiftUI

struct ScenarioView: View {
    @State var showScenarioSetting : Bool = false // 회원가입 팝업 표시 여부 추가
    @State var showAlert : Bool = false
    
    var body: some View {
        ZStack {
            VStack(spacing: 30) {
                HStack {
                    
                    Button (action : {
                        showScenarioSetting.toggle()
                    }) {
                        VStack {
                            Spacer()
                            
                            Image(systemName: "bed.double.fill")
                                .font(.system(size: 75))
                            
                            Spacer()
                            
                            Text("수면")
                                .padding(.bottom, 10)
                        }
                    }
                    .frame(width: 150, height: 150)
                    .border(.black, width: 1.5)
                    .cornerRadius(3)
                    .foregroundColor(.black)
                    .shadow(radius: 5, x: 5, y: 5)
                    
                    Spacer()
                    
                    Button (action : {
                        showScenarioSetting.toggle()
                    }) {
                        VStack {
                            Spacer()
                            
                            Image(systemName: "fork.knife")
                                .font(.system(size: 75))
                            
                            Spacer()
                            
                            Text("식사")
                                .padding(.bottom, 10)
                        }
                    }
                    .frame(width: 150, height: 150)
                    .border(.black, width: 1.5)
                    .cornerRadius(3)
                    .foregroundColor(.black)
                    .shadow(radius: 5, x: 5, y: 5)
                }
                
                HStack {
                    Button (action : {
                        showScenarioSetting.toggle()
                    }) {
                        VStack {
                            Spacer()
                            
                            Image(systemName: "list.clipboard")
                                .font(.system(size: 75))
                            
                            Spacer()
                            
                            Text("학습")
                                .padding(.bottom, 10)
                        }
                        
                    }
                    .frame(width: 150, height: 150)
                    .border(.black, width: 1.5)
                    .cornerRadius(3)
                    .foregroundColor(.black)
                    .shadow(radius: 5, x: 5, y: 5)
                    
                    Spacer()
                }
                
                Spacer()
            }
            .padding(.horizontal, 30)
            
            if showScenarioSetting {
                if #available(iOS 15.0, *) {
                    ScenarioSettingView(showScenarioSetting: $showScenarioSetting, showAlert: $showAlert)
                } else {
                    // Fallback on earlier versions
                }

//                    .edgesIgnoringSafeArea(.all)
//                    .background(Color.black.opacity(0.4))
            }
        }
        .alert(isPresented: $showAlert) {
            Alert(title: Text("시나리오 설정값이 변경되었습니다."), message: nil,
                          dismissButton: .default(Text("확인")))
        }
    }
}

@available(iOS 15.0, *)
struct ScenarioSettingView: View {
    @Binding var showScenarioSetting: Bool
    @Binding var showAlert : Bool
    @State private var selectedColor: Color = .white
    @State private var brightness: Double = 1.0
    let predefinedColors: [Color] = [.red, .orange, .yellow, .green, .blue, .indigo, .purple]
    
    var body: some View {
        VStack {
            VStack(spacing: 20) {
                // 시나리오 텍스트
                Spacer()
                
                Text("시나리오 : 수면")
                    .font(.title2)
                    .fontWeight(.semibold)
                    .padding(.top, 10)
                
                // 컬러 피커 (Color Wheel)
                ColorPicker("색상 선택", selection: $selectedColor, supportsOpacity: false)
                    .labelsHidden()
                    .scaleEffect(2.0) // 크기 조절
                    .frame(width: 200, height: 200)
                
                HStack {
                    ForEach(predefinedColors, id: \.self) { color in
                        Button(action: {
                            selectedColor = color
                        }) {
                            Circle()
                                .fill(color)
                                .frame(width: 30, height: 30)
                        }
                    }
                }
                
                // 밝기 슬라이더
                VStack {
                    Slider(value: $brightness, in: 0...1)
                        .accentColor(.blue)
                        .padding(.horizontal, 30)
                    
                    Text("조도 : \(Int(brightness * 100))")
                        .font(.headline)
                }
                
                // 설정값 변경 버튼
                Button(action: {
                    showAlert.toggle()
                    showScenarioSetting.toggle()
                    print("설정값이 변경되었습니다.")
                }) {
                    Text("설정값 변경")
                        .font(.body)
                        .foregroundColor(.blue)
                        .padding()
                }
                
                
                Spacer()
            }
            .frame(width: 325, height: 500)
            .background(Color.white)
            .cornerRadius(20)
            .shadow(radius: 10)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

}
/*
struct ScenarioSettingView: View {
    @Binding var showScenarioSetting: Bool
    @State private var selectedColor: Color = .blue

    var body: some View {
        VStack {
            Spacer()
            
            VStack(spacing: 20) {
                Text("시나리오 : ")
                    .font(.title)
                    .fontWeight(.bold)
                    .padding(.top, 20)
                
                ColorPicker("Choose a color", selection: $selectedColor)
                                .padding()
                
                Button(action: {
                    showScenarioSetting = false
                }) {
                    Text("확인")
                        .fontWeight(.bold)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                }
                .padding(.horizontal, 20)
                .padding(.bottom, 20)
            }
            .frame(width: 300)
            .background(Color.white)
            .cornerRadius(20)
            .shadow(radius: 10)
            
            Spacer()
        }
        .frame(maxWidth: .infinity)
    }
}
*/
#Preview {
    ScenarioView()
}

