//
//  LightSettingView.swift
//  bulls
//
//  Created by 차차 on 10/4/24.
//

import SwiftUI

struct LightSettingView: View {
    @State private var onOffToggle = true
    @State private var recognitionToggle = true
    @State private var brightness: Double = 0.1
    @State private var selectedColor: Color = .yellow
    @State private var showLightColorSetting = false
    @State private var isEditing: Bool = false
    @State private var isBrightnessChanged = false
    @Binding var showAlert : Bool

    var body: some View {
        NavigationView {
            ZStack {
                VStack(spacing :20) {
                VStack(spacing: 20) {
                    Toggle("전원", isOn: $onOffToggle)
                }
                .padding(.horizontal, 15)
                .padding(.top, 10)
                
                ZStack {
                    VStack(spacing: 50) {
                    
                    Button(action: {
                        showLightColorSetting.toggle()
                    }, label: {
                        Image(systemName: "lightbulb.fill")
                            .resizable()
                            .aspectRatio(contentMode: .fit)
                            .frame(width: 200, height: 200)
                            .foregroundColor(selectedColor.opacity(brightness))
                            .padding()
                    })
                    
                    
                    
                        VStack(spacing : 20) {
                        Slider(value: $brightness, in: 0...1, step: 0.01
                        ,onEditingChanged: { editing in
                            isEditing = editing
                            if !editing {
                                // 값 변경 완료 시 이벤트 처리
                                Task {
                                    isBrightnessChanged = true
                                }
                            }
                        }
                        )
                            .accentColor(.blue)
                            .padding(.horizontal, 30)
                        
                        Text("조도 : \(Int(brightness * 100))")
                            .font(.headline)
                        
                            if #available(iOS 15.0, *) {
                                Button("조도 변경"){
                                    //                            showLightColorSetting.toggle()
                                    if isBrightnessChanged {
                                        isBrightnessChanged = false
                                        DispatchQueue.main.asyncAfter(deadline: DispatchTime.now() + 0.5) {
                                            showAlert.toggle()
                                        }
                                    }
                                }
                                .buttonStyle(.borderedProminent)
                                .padding(.vertical, 25)
                            } else {
                                // Fallback on earlier versions
                            }
                    }
                    .padding(.bottom, 10)
                }
                .overlay(
                    ZStack {
//                        Text("조명의 전원이 꺼졌습니다.")
                        
                        Rectangle()
                            .opacity(onOffToggle && recognitionToggle ? 0 : 0.4)
                        
                        if #available(iOS 17.0, *) {
                            Text("조명의 전원이 꺼졌습니다.")
                                .foregroundStyle(.white)
                                .font(.title)
                                .opacity(onOffToggle && recognitionToggle ? 0 : 1)
                        } else {
                            // Fallback on earlier versions
                        }
                    }
                )
                }
                
                Spacer()
            }
                if showLightColorSetting {
                    if #available(iOS 15.0, *) {
                        LightColorSettingView(showLightColorSetting: $showLightColorSetting, selectedColor: $selectedColor, showAlert: $showAlert)
                    } else {
                        // Fallback on earlier versions
                    }
                }
            }
        }
    }
}

@available(iOS 15.0, *)
struct LightColorSettingView: View {
    @Binding var showLightColorSetting: Bool
    @Binding var selectedColor: Color
    @Binding var showAlert : Bool
    @State private var brightness: Double = 0.5
    let predefinedColors: [Color] = [.red, .orange, .yellow, .green, .blue, .indigo, .purple]
    
    var body: some View {
        VStack {
            VStack(spacing: 20) {
                // 시나리오 텍스트
                Spacer()
                
                Text("조명 색상 변경하기")
                    .font(.title2)
                    .fontWeight(.semibold)
                    .padding(.top, 10)
                
                
                ColorPicker("색상 선택", selection: $selectedColor, supportsOpacity: false)
                    .labelsHidden()
                    .scaleEffect(2.0)
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
                
                // 설정값 변경 버튼
                Button(action: {
                    showLightColorSetting.toggle()
                    DispatchQueue.main.asyncAfter(deadline: DispatchTime.now() + 0.5) {
                        showAlert.toggle()
                    }
                    
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

//#Preview {
//    LightSettingView()
//}
