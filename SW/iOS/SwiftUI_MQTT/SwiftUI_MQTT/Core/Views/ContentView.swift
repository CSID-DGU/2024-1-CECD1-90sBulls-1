//
//  ContentView.swift
//  SwiftUI_MQTT
//
//  Created by 차차 on 11/27/24.
//

import SwiftUI

struct ContentView: View {
    @EnvironmentObject private var mqttManager: MQTTManager
    @State var brightness = 0.1
    @State var red = 0
    @State var green = 0
    @State var blue = 0
    @State private var selectedOption = "0"
    @State private var isEditing: Bool = false
    @State private var selectedTab: Int = 0
    @State private var showAlert = false
    
    @State private var onOffToggle = true
    @State private var recognitionToggle = true
//    @State private var brightness: Double = 0.1
    @State private var selectedColor: Color = .yellow
    @State private var showLightColorSetting = false
//    @State private var isEditing: Bool = false
    @State private var isBrightnessChanged = false
    
    let options = ["0", "2", "3"]
    
    let formatter: NumberFormatter = {
        let formatter = NumberFormatter()
        formatter.numberStyle = .decimal
        return formatter
    }()
    
    @State var isLaunching: Bool = true
    /*
    var body: some View {
        if isLaunching {
            SplashView()
                .onAppear {
                    DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
                        isLaunching = false
                    }
                }
        } else {
            if #available(iOS 15.0, *) {
                ZStack {
                    if #available(iOS 15.0, *) {
                        Rectangle()
                            .foregroundStyle(Color.blue)
                            .ignoresSafeArea()
                    } else {
                        // Fallback on earlier versions
                    }
                    
                        VStack {
                            Text("\(mqttManager.connectionStateMessage())")
                            Text("스마트 조명 관리 시스템")
                                .foregroundStyle(Color.white)
                                .font(.system(size: 20, weight: .black))
                                .padding(.vertical, 20)
                            
                            VStack(spacing: 30) {
                                HStack(spacing: 0) {
                                    Button(action: {
                                        selectedTab = 0
                                    }) {
                                        Text("현재 조명")
                                            .foregroundStyle(.black)
                                            .frame(maxWidth: .infinity)
                                            .padding(10)
                                            .background(selectedTab == 0 ? Color.white : Color.white.opacity(0.5))
                                            .cornerRadius(25, corners: [.topLeft, .topRight])
                                    }
                                    
                                    Button(action: {
                                        selectedTab = 1
                                    }) {
                                        Text("시나리오")
                                            .foregroundStyle(.black)
                                            .frame(maxWidth: .infinity)
                                            .padding(10)
                                            .background(selectedTab == 1 ? Color.white : Color.white.opacity(0.5))
                                            .cornerRadius(25, corners: [.topLeft, .topRight])
                                        
                                    }
                                }
                                .background(Color.blue)
                                
                                VStack {
                                    if selectedTab == 0 {
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
                                                    
                                                    do {
                                                        let data = """
                                                        {
                                                            "lx" : \(brightness),
                                                            "r" : \(red),
                                                            "g" : \(green),
                                                            "b" : \(blue)
                                                        }
                                                        """.data(using:.utf8)!
                                                    
                                                        let jsonString = String(data: data, encoding: .utf8) ?? "failed to encode json"
                                                    
                                                        send(topic: "app/light", message: jsonString)
                                                    } 
                                                    catch {
                                                        print("Error encoding JSON: \(error)")
                                                    }
                                                    
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
                                                                    Task {
                                                                        await sendValueToPi(brightness)
                                                                    }
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
                                                    LightColorSettingView(showLightColorSetting: $showLightColorSetting, selectedColor: $selectedColor, showAlert: $showAlert, red: $red, green: $green, blue: $blue, brightness: $brightness)
                                                } else {
                                                    // Fallback on earlier versions
                                                }
                                            }
                                        }
                                            .padding(.horizontal, 5)
                                    }
                                    else {
                                        ScenarioView()
                                            .padding(.horizontal, 5)
                                    }
                                }
                                .background(Color.white)
                            }
                            .background(Color.white)
                        }
                    }
                .alert(isPresented: $showAlert) {
                    Alert(title: Text("조명의 설정 값이 변경 되었습니다."), message: nil,
                                  dismissButton: .default(Text("확인")))
                }
            } else {
                Text("version up")
            }
        }
    }
    */
    struct SplashView: View {
        
        var body: some View {
            ZStack {
                Color(red: 0.08, green: 0.33, blue: 0.97)
                    .ignoresSafeArea()
                Text("스마트 조명 관리 시스템")
                    .font(
                    Font.custom("Montserrat", size: 20)
                    .weight(.semibold)
                    )
                    .foregroundColor(.white)
            }
        }
    }
    
    @available(iOS 15.0, *)
    struct LightColorSettingView: View {
        @Binding var showLightColorSetting: Bool
        @Binding var selectedColor: Color
        @Binding var showAlert : Bool
        @Binding var red : Int
        @Binding var green : Int
        @Binding var blue : Int
        @Binding var brightness: Double
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
    
    var body: some View {
        VStack(spacing: 50) {
            Text("조명과의 연결 상태 : \(mqttManager.connectionStateMessage())")
            
            // 색상 변경
            VStack {
                HStack {
                    Text("색상 변경")
                        .font(.title2)
                    
                    Spacer()
                }
                HStack {
                    Text("R: ")
                    TextField("R", value: $red, formatter: formatter)
                        .keyboardType(.decimalPad)
                    Text("G: ")
                    TextField("G", value: $green ,formatter: formatter)
                        .keyboardType(.decimalPad)
                    Text("B: ")
                    TextField("B", value: $blue, formatter: formatter)
                        .keyboardType(.decimalPad)
                }
                
                Button(action: {
                    do {
                        let data = """
                        {
                            "lx" : \(brightness),
                            "r" : \(red),
                            "g" : \(green),
                            "b" : \(blue)
                        }
                        """.data(using:.utf8)!

                        let jsonString = String(data: data, encoding: .utf8) ?? "failed to encode json"

                        send(topic: "app/light", message: jsonString)
                    } catch {
                        print("Error encoding JSON: \(error)")
                    }
                }) {
                    Text("색상 변경")
                }
            }
            
            // 조도 조절
            VStack {
                HStack {
                    Text("조도 조절")
                        .font(.title2)
                    
                    Spacer()
                }
                Slider(value: $brightness, in: 0 ... 100, step: 1,
                       onEditingChanged: { editing in
                           isEditing = editing
                           if !editing {
                               // 값 변경 완료 시 이벤트 처리
                               Task {
                                   await sendValueToPi(brightness)
                               }
                           }
                       })
//                    .onChange(of: brightness) { newValue in
//                        Task {
//                            await sendValueToPi(newValue)
//                        }
//                    }
                Text("조도 : \(brightness, specifier: "%.f")")
            }
            /*
            VStack {
                HStack {
                    Text("시나리오 설정 변경")
                        .font(.title2)
                    
                    Spacer()
                }
                
                VStack(spacing: 15) {
                    
                    Picker("시나리오", selection: $selectedOption) {
                        ForEach(options, id: \.self) { option in
                            Text(option)
                        }
                    }
                    
                    HStack {
                        Text("R: ")
                        TextField("R", value: $r_scenario, formatter: formatter)
                            .keyboardType(.decimalPad)
                        Text("G: ")
                        TextField("G", value: $g_scenario ,formatter: formatter)
                            .keyboardType(.decimalPad)
                        Text("B: ")
                        TextField("B", value: $b_scenario, formatter: formatter)
                            .keyboardType(.decimalPad)
                    }
                    
                    Slider(value: $brightness_scenario, in: 0 ... 100, step: 1)
                    Text("조도 : \(brightness_scenario, specifier: "%.f")")
                    
                    Button(action: {
                        do {
                            let data = """
                            {
                                "lx" : \(brightness_scenario),
                                "r" : \(r_scenario),
                                "g" : \(g_scenario),
                                "b" : \(b_scenario)
                            }
                            """.data(using:.utf8)!

                            let jsonString = String(data: data, encoding: .utf8) ?? "failed to encode json"

                            send(topic: "app/scenario", message: jsonString)
                        } catch {
                            print("Error encoding JSON: \(error)")
                        }
                    }) {
                        Text("시나리오 설정 변경")
                    }
                    
                }
                .padding(.horizontal, 20)
                
            }
            */
            Spacer()
        }
        .padding()
        .onAppear() {
            mqttManager.initializeMQTT(host: "broker.hivemq.com", identifier: UUID().uuidString)
            mqttManager.connect()
        }
    }
    
    private func send(topic: String, message: String) {
        let finalMessage = "\(message)"
        mqttManager.publish(topic: topic, with: finalMessage)
    }
    
    func sendValueToPi(_ value: Double) async {
            do {
                let data = """
                {
                    "lx" : \(brightness),
                    "r" : \(red),
                    "g" : \(green),
                    "b" : \(blue)
                }
                """.data(using:.utf8)!

                let jsonString = String(data: data, encoding: .utf8) ?? "failed to encode json"

                send(topic: "app/light", message: jsonString)
            } catch {
                print("Error encoding JSON: \(error)")
            }
        }
}


//#Preview {
//    ContentView()
//        .environmentObject(mqttManager)
//}
