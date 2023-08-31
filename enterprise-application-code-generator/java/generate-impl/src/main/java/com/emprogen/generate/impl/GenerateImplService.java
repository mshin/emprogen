package com.emprogen.generate.impl;

import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.lang.reflect.Parameter;
import java.lang.reflect.Type;

public class GenerateImplService {

    public static void main(String[] args) {
        System.out.println(generateClass(args[0], args[1]));
    }

    public static Class<?> loadClass(String className) throws RuntimeException, NullPointerException {
        boolean isLoaded = true;
        Class<?> clazz = null;
        try {
            clazz = Class.forName(className);
        } catch (ClassNotFoundException e) {
            System.err.println("class not found: " + e);
            isLoaded = false;
        }

        if (null == clazz) {
            isLoaded = false;
        }
        // System.out.println("class is loaded: " + isLoaded);
        return clazz;
    }

    public static String generateClass(String className, String newPackage) {
        Class<?> iclazz = loadClass(className);

        if (!iclazz.isInterface()) {
            String message = "class " + className + " is not an interface.";
            System.err.println(message);
            throw new IllegalArgumentException(message);
        }

        StringBuilder sb = new StringBuilder();

        sb.append("package ");
        sb.append(newPackage);
        sb.append(";\n\n");
        sb.append("public class ");
        sb.append(iclazz.getSimpleName());
        sb.append("Bean");
        sb.append(" implements ");
        sb.append(iclazz.getName());
        sb.append(" {\n\n");
        Method[] methods = iclazz.getMethods();
        for (Method m : methods) {
            if (!m.isDefault()) {
                sb.append("    @Override\n");
                sb.append(createMethodString(m));
            }
        }

        sb.append("}\n");
        return sb.toString();
    }

    public static String createMethodString(Method method) {
        StringBuilder sb = new StringBuilder();

        int mod = method.getModifiers();
        if (Modifier.isAbstract(mod)) {
            mod = mod - Modifier.ABSTRACT;
        }
        String accessModifier = Modifier.toString(mod);

        Type returnType = method.getGenericReturnType();
        String returnTypeS = returnType.getTypeName();
        String methodName = method.getName();
        Parameter[] parameters = method.getParameters();

        Type[] exceptionTypes = method.getGenericExceptionTypes();

        sb.append("    ");
        sb.append(accessModifier);
        sb.append(" ");
        sb.append(returnTypeS);
        sb.append(" ");
        sb.append(methodName);
        sb.append("(");

        for (int i = 0; i < parameters.length; i++) {
            Parameter p = parameters[i];
            if (0 != i) {
                sb.append(", ");
            }
            String modifiers = Modifier.toString(p.getModifiers());
            // only final modifier permitted; lost after compile, so never any modifiers.
            if (null != modifiers && "" != modifiers) {
                sb.append(modifiers);
                sb.append(" ");
            }

            sb.append(p.getType().getTypeName());
            sb.append(" ");
            sb.append(p.getName());
        }

        sb.append(")");
        if (0 < exceptionTypes.length) {
            sb.append(" throws");
            for (int i = 0; i < exceptionTypes.length; i++) {
                Type t = exceptionTypes[i];
                if (0 != i) {
                    sb.append(",");
                }
                sb.append(" ");
                sb.append(t.getTypeName());
            }
        }
        sb.append(" {\n");
        if (!"void".equals(returnTypeS)) {
            sb.append("        return null;\n");
        }
        sb.append("    }\n");
        return sb.toString();
    }

}